"""对话相关请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """新建会话请求体。"""

    title: str = Field(default="新对话", max_length=200, description="会话标题")
    first_message: str | None = Field(
        default=None, min_length=1, max_length=4000, description="首条消息内容"
    )


class MessageCreate(BaseModel):
    """发送消息请求体。"""

    content: str = Field(min_length=1, max_length=4000, description="消息内容")


class MessageOut(BaseModel):
    """消息响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ConversationOut(BaseModel):
    """会话列表项响应体（不含消息）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetail(ConversationOut):
    """会话详情响应体（含消息列表）。"""

    messages: list[MessageOut]


class MessageExchange(BaseModel):
    """发送消息后的响应：用户消息 + 模拟 AI 回复。"""

    user_message: MessageOut
    assistant_message: MessageOut
