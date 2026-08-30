"""密码哈希与 JWT 令牌工具。

- 密码哈希：PBKDF2-SHA256（标准库实现，带随机盐，无第三方依赖兼容性问题）
- 令牌：PyJWT 签发/校验 HS256 签名的 JWT
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings

_PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """对明文密码做加盐 PBKDF2 哈希，返回可存储的字符串。"""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """校验明文密码与存储的哈希是否匹配。"""
    try:
        _, iterations, salt, expected = hashed_password.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        )
        return secrets.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """签发 JWT，subject 一般为用户 ID 的字符串形式。"""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """解码并校验 token，返回 subject（用户 ID）；无效时返回 None。"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
