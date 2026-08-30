"""令牌相关 Schema。"""

from pydantic import BaseModel


class Token(BaseModel):
    """登录成功返回的访问令牌。"""

    access_token: str
    token_type: str = "bearer"
