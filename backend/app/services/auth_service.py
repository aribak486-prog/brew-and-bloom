from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import hash_password


def register_user(db: Session, payload: UserCreate) -> User:
    email = str(payload.email).lower()
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password), role=UserRole.CUSTOMER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))
