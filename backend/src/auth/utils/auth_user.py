from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import user as db_user
from src.auth.utils.password_manager import PasswordManager
from src.auth.utils.jwt_manager import JWTManager


async def login_user(cred_data: dict, session: AsyncSession):
    query = select(db_user).where(db_user.c.email == cred_data['email'])
    user = (await session.execute(query)).fetchone()

    if not user or not user.is_active or not await PasswordManager.verify_password(cred_data['password'], user.hashed_password):
        raise HTTPException(status_code=400, detail='Invalid credintials')

    response = JWTManager().get_login_response_with_cookie(user_id=str(user.id))

    return response


async def logout_user():
    response = JWTManager().get_logout_response_with_cookie()

    return response
