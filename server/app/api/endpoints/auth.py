"""登录、注册、当前用户信息接口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.crud import user as user_crud
from app.db.base import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter()

# OAuth2 密码模式：Swagger 文档的 Authorize 按钮将使用此地址获取令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _find_user_by_account(db: Session, account: str) -> User | None:
    """通过用户名或邮箱查找用户。"""
    user = user_crud.get_by_username(db, account)
    if user is None:
        user = user_crud.get_by_email(db, account)
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """用户注册。"""
    if user_crud.get_by_username(db, payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已被注册")
    if user_crud.get_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册")

    user = user_crud.create_user(db, payload, hash_password(payload.password))
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """登录，返回 JWT 访问令牌。

    请求体为标准 OAuth2 表单（application/x-www-form-urlencoded）：
    username 字段支持用户名或邮箱，password 为密码。
    """
    user = _find_user_by_account(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """依赖：从请求头 Authorization: Bearer <token> 解析当前登录用户。"""
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """获取当前登录用户信息（需要携带 Bearer 令牌）。"""
    return current_user
