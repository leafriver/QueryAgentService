"""对话（会话与消息）接口。

- 所有操作仅限当前登录用户本人数据，访问他人会话统一返回 404
- AI 回复由大模型服务层生成（ModelScope OpenAI 兼容接口），
  调用失败时返回兜底文案，不影响接口可用性
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud import conversation as conversation_crud
from app.db.base import get_db
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    MessageCreate,
    MessageExchange,
)
from app.services.llm import LLMError, build_messages, chat_completion, chat_completion_stream

logger = logging.getLogger(__name__)

router = APIRouter()


def _history_to_messages(db: Session, conversation_id: int) -> list[dict]:
    """读取会话历史并构造发给模型的 messages（含系统提示，超长截断）。"""
    history = conversation_crud.get_history_messages(db, conversation_id)
    return build_messages(
        [
            {"role": message.role, "content": message.content}
            for message in history
            if message.role in ("user", "assistant")
        ]
    )


def _sse(payload: dict) -> str:
    """将 JSON 数据编码为一条 SSE 事件文本。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _generate_reply(db: Session, conversation_id: int) -> str:
    """基于会话历史调用真实大模型生成回复；失败时返回兜底文案。"""
    messages = _history_to_messages(db, conversation_id)
    try:
        return chat_completion(messages)
    except LLMError as exc:
        logger.warning("LLM 调用失败（会话 %s）: %s", conversation_id, exc)
        return (
            "抱歉，AI 服务暂时不可用，请稍后重试。\n\n"
            "> 错误详情："
            f"{exc}\n\n"
            "你可以检查网络连接，或确认 ModelScope Token 是否有效。"
        )


def _get_owned_conversation(db: Session, conversation_id: int, user: User) -> Conversation:
    """获取属于当前用户的会话，越权或不存在时抛出 404。"""
    conversation = conversation_crud.get_user_conversation(db, conversation_id, user.id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return conversation


@router.post("", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conversation:
    """新建会话；携带 first_message 时同时生成一条真实 AI 回复。"""
    conversation = conversation_crud.create_conversation(
        db, current_user.id, payload.title
    )
    if payload.first_message:
        conversation_crud.add_message(db, conversation, "user", payload.first_message)
        reply = _generate_reply(db, conversation.id)
        conversation_crud.add_message(db, conversation, "assistant", reply)
    db.refresh(conversation)
    return conversation


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Conversation]:
    """当前用户的会话列表（按更新时间倒序）。"""
    return conversation_crud.list_user_conversations(db, current_user.id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conversation:
    """会话详情（含消息列表）。"""
    return _get_owned_conversation(db, conversation_id, current_user)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """删除会话（其下消息级联删除）。"""
    conversation = _get_owned_conversation(db, conversation_id, current_user)
    conversation_crud.delete_conversation(db, conversation)


@router.post("/{conversation_id}/messages", response_model=MessageExchange)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageExchange:
    """发送消息：保存用户消息并返回真实 AI 回复。"""
    conversation = _get_owned_conversation(db, conversation_id, current_user)
    user_message = conversation_crud.add_message(
        db, conversation, "user", payload.content
    )
    reply = _generate_reply(db, conversation.id)
    assistant_message = conversation_crud.add_message(
        db, conversation, "assistant", reply
    )
    return MessageExchange(
        user_message=user_message, assistant_message=assistant_message
    )


@router.post("/{conversation_id}/messages/stream")
def send_message_stream(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """发送消息并流式返回 AI 回复（SSE，逐字输出）。

    SSE 事件契约（每条以空行分隔）：
        data: {"type": "delta", "content": "文本增量"}
        data: {"type": "done", "message_id": N}
        data: {"type": "error", "detail": "错误信息"}

    正常结束时将完整回复落库；客户端中断（如点击停止）时保存已生成部分。
    """
    conversation = _get_owned_conversation(db, conversation_id, current_user)
    conversation_crud.add_message(db, conversation, "user", payload.content)
    messages = _history_to_messages(db, conversation.id)

    def event_stream():
        collected: list[str] = []
        try:
            for delta in chat_completion_stream(messages):
                collected.append(delta)
                yield _sse({"type": "delta", "content": delta})

            content = "".join(collected).strip()
            if not content:
                raise LLMError("模型返回了空内容，请重试")

            assistant_message = conversation_crud.add_message(
                db, conversation, "assistant", content
            )
            yield _sse({"type": "done", "message_id": assistant_message.id})
        except GeneratorExit:
            # 客户端中断（如点击停止）：保存已生成的部分回复
            partial = "".join(collected).strip()
            if partial:
                try:
                    conversation_crud.add_message(
                        db, conversation, "assistant", partial
                    )
                except Exception:  # noqa: BLE001
                    logger.exception("保存中断回复失败（会话 %s）", conversation.id)
            raise
        except LLMError as exc:
            logger.warning("LLM 流式调用失败（会话 %s）: %s", conversation.id, exc)
            yield _sse({"type": "error", "detail": str(exc)})
        except Exception:  # noqa: BLE001
            logger.exception("流式对话接口异常（会话 %s）", conversation.id)
            yield _sse({"type": "error", "detail": "服务内部错误，请稍后重试"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
