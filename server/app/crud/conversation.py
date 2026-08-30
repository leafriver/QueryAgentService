"""会话与消息表的数据访问层。"""

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


def create_conversation(db: Session, user_id: int, title: str = "新对话") -> Conversation:
    """创建会话并提交。"""
    conversation = Conversation(user_id=user_id, title=title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversation(
    db: Session, conversation_id: int, user_id: int
) -> Conversation | None:
    """获取属于指定用户的某次会话（含消息），不存在或归属不符返回 None。"""
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .first()
    )


def list_user_conversations(db: Session, user_id: int) -> list[Conversation]:
    """当前用户的会话列表，按更新时间倒序（不加载消息，避免 N+1）。"""
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        .all()
    )


def delete_conversation(db: Session, conversation: Conversation) -> None:
    """删除会话（其下消息由 ORM 级联删除）。"""
    db.delete(conversation)
    db.commit()


def add_message(
    db: Session, conversation: Conversation, role: str, content: str
) -> Message:
    """向会话追加一条消息，并刷新会话更新时间。"""
    message = Message(conversation_id=conversation.id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_history_messages(db: Session, conversation_id: int) -> list[Message]:
    """按时间正序返回会话的全部消息，用于构造模型上下文。"""
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .all()
    )
