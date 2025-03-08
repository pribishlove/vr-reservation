from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from datetime import datetime
from src.models.settings import settings
from src.models.bookings import booking
from src.models.headsets import headset
from src.models.users import user
from src.schemas.user_schema import UserSchema
from src.schemas.settings_schema import ChangeAutoconfirmSchema
from src.schemas.booking_schema import ResponseBookingSchema
from src.schemas.headset_schema import ChangeCostSchema
from src.auth.utils.jwt_manager import get_current_superuser
from src.utils.booking_utils import get_headset_name, change_booking_status, send_email
from src.utils.convert_time import convert_time
from sqlalchemy import select, update, and_


router = APIRouter()


@router.get(
    '/autoconfirm',
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def get_autoconfirm(
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    query = select(settings.c.auto_confirm)
    auto_confirm = (await session.execute(query)).fetchone()

    if not auto_confirm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Autoconfirm setting is not set')
    
    auto_confirm = auto_confirm[0]

    return {'autoconfirm': auto_confirm}


@router.post(
    '/autoconfirm',
    status_code=status.HTTP_204_NO_CONTENT
)
async def post_autoconfirm(
    autoconfirm_data: ChangeAutoconfirmSchema,
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    query = select(settings.c.auto_confirm)
    auto_confirm = (await session.execute(query)).fetchone()

    if not auto_confirm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Autoconfirm setting is not set')
    
    auto_confirm = auto_confirm[0]

    if autoconfirm_data.autoconfirm == auto_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Autoconfirm setting is already {auto_confirm}')

    stmt = update(
        settings
    ).values(
        auto_confirm=autoconfirm_data.autoconfirm
    )

    await session.execute(stmt)
    await session.commit()

    return


@router.get(
    '/for_confirm',
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def get_bookings_for_confirm(
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    local_time_now = convert_time(datetime.now())
    query = select(
        booking
    ).where(
        and_(
            booking.c.status == 'pending',
            booking.c.start_time > local_time_now
        )
    )

    bookings = (await session.execute(query)).fetchall()

    if not bookings:
        return {'result': []}

    result = [
        ResponseBookingSchema(
            booking_id=current_booking.id,
            headset_name=await get_headset_name(current_booking.headset_id, session),
            cost=current_booking.cost,
            start_time=current_booking.start_time,
            end_time=current_booking.end_time,
            status=current_booking.status
        ) for current_booking in bookings
    ]
    
    return {"result": result}


@router.post(
    '/{booking_id}/confirm',
    status_code=status.HTTP_204_NO_CONTENT
)
async def confirm_booking(
    booking_id: int, 
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    return await change_booking_status(booking_id, session, current_user, 'confirmed')


@router.post(
    '/{booking_id}/cancel',
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_booking(
    booking_id: int, 
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    return await change_booking_status(booking_id, session, current_user, 'cancelled')


@router.post(
    '/change_cost',
    status_code=status.HTTP_204_NO_CONTENT
)
async def change_cost(
    cost_data: ChangeCostSchema, 
    current_user: UserSchema = Depends(get_current_superuser),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    query = select(
        headset
    ).where(
        headset.c.id == cost_data.headset_id,
    )
    current_headset = (await session.execute(query)).fetchone()
    old_cost = current_headset.cost
    
    if not current_headset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Headset not found')
    if old_cost == cost_data.new_cost:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Headset cost is already {cost_data.new_cost}')
    
    stmt = update(
        headset
    ).where(
        headset.c.id == cost_data.headset_id,
    ).values(
        cost=cost_data.new_cost
    )

    await session.execute(stmt)
    await session.commit()

    if cost_data.new_cost < old_cost:
        query = select(user.c.email).where(user.c.is_subscribed_to_email == True)
        user_emails = (await session.execute(query)).fetchall()
        for user_email in user_emails:
            await send_email(
                'notice',
                user_email[0],
                await get_headset_name(cost_data.headset_id, session),
                cost_data.new_cost,
                old_cost
            )

    return 
