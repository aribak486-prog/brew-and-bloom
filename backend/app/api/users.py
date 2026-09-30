from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def current_profile(user: User = Depends(get_current_user)):
    return {"success": True, "data": UserPublic.model_validate(user)}
