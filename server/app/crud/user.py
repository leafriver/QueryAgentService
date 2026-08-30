"""用户表的数据访问层。"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate, hashed_password: str) -> User:
    """创建用户，密码以哈希形式存储。"""
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
