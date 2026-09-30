from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token, verify_password
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserPublic
from app.services.auth_service import find_user_by_email, register_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if find_user_by_email(db, str(payload.email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    try:
        user = register_user(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    return {"success": True, "data": UserPublic.model_validate(user)}


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = find_user_by_email(db, str(payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    data = TokenResponse(access_token=create_access_token(str(user.id)), user=UserPublic.model_validate(user))
    return {"success": True, "data": data}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"success": True, "data": UserPublic.model_validate(user)}
