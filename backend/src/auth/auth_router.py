from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schema import UserCreate, UserLogin
from src.auth.utils.create_user import create_user
from src.auth.utils.auth_user import login_user, logout_user
from config.database import get_async_session


router = APIRouter()

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    return await create_user(user_create.dict(), session)


@router.post(
    "/login",
    status_code=status.HTTP_204_NO_CONTENT
)
async def login(
    user_login: UserLogin,
    session: AsyncSession = Depends(get_async_session)
):
    return await login_user(user_login.dict(), session)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout():
    return await logout_user()
