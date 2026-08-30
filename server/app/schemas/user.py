"""用户相关请求/响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """注册请求体。"""

    username: str = Field(min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(min_length=6, max_length=128, description="密码，至少 6 位")


class UserLogin(BaseModel):
    """登录请求体（JSON 方式，供前端可选使用）。"""

    username: str = Field(description="用户名或邮箱")
    password: str = Field(description="密码")


class UserOut(BaseModel):
    """用户信息响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
