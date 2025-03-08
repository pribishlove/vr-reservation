from fastapi import APIRouter, status, Depends

from src.schemas.user_schema import UserSchema
from src.auth.utils.jwt_manager import get_current_user, get_current_superuser


router = APIRouter()

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserSchema
)
async def get_me(
    user: UserSchema = Depends(get_current_user)
):
    return user


