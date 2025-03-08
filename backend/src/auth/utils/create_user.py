from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users import user
from src.auth.utils.password_manager import PasswordManager
from config.database import async_session_maker
from config.config import ADMIN_EMAIL, ADMIN_PASSWORD


async def create_user(user_dict: dict, session: AsyncSession):
    password = user_dict.pop('password')

    if not await PasswordManager.validate_password(password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The password must be at least 6 characters long")
    
    query = select(user).where(user.c.email == user_dict['email'])
    result = await session.execute(query)

    if result.fetchone():
        if user_dict['email'] == ADMIN_EMAIL:
            return
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email alredy exists")
    
    hashed_password = await PasswordManager.get_hashed_password(password)

    is_superuser: bool = False if user_dict['email'] != ADMIN_EMAIL else True

    try:
        stmt = insert(user).values(
            email=user_dict['email'],
            hashed_password=str(hashed_password),
            is_active=True,
            is_superuser=is_superuser,
            is_subscribed_to_email=False
        )
        
        await session.execute(stmt)
        await session.commit()

        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


async def create_admin_user() -> None:
    async with async_session_maker() as session:
        result = await create_user(
            user_dict={
                'email': ADMIN_EMAIL,
                'password': ADMIN_PASSWORD
            },
            session=session
        )
    if result:
        print('admin account created')
