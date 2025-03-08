from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from src.models.users import user
from src.schemas.email_schema import ChangeSubscriptionSchema
from src.schemas.user_schema import UserSchema
from src.auth.utils.jwt_manager import get_current_user
from sqlalchemy import update


router = APIRouter()


@router.post(
    '/subscription',
    status_code=status.HTTP_204_NO_CONTENT
)
async def post_subscription(
    sub_data: ChangeSubscriptionSchema,
    current_user: UserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    is_subscribed_to_email = sub_data.is_subscribed_to_email

    if current_user.is_subscribed_to_email == is_subscribed_to_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Subscription is already {is_subscribed_to_email}')
    
    stmt = update(
        user
    ).where(
        user.c.id == current_user.id
    ).values(
        is_subscribed_to_email=is_subscribed_to_email
    )

    await session.execute(stmt)
    await session.commit()

    return
