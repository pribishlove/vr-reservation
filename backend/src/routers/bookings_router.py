from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from src.models.bookings import booking
from src.models.settings import settings
from src.schemas.booking_schema import BookingTimeSchema, BookingCreateSchema, ResponseBookingSchema
from src.schemas.user_schema import UserSchema
from src.auth.utils.jwt_manager import get_current_user
from src.utils.convert_time import convert_time
from src.utils.booking_utils import get_headset_name, change_booking_status, get_cost, send_email
from sqlalchemy import select, insert, and_
from datetime import datetime, date


router = APIRouter()


@router.get(
    "/my",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def get_my_bookings(
    user: UserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    query = select(
        booking
    ).where(
        booking.c.user_id == user.id
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
    '/{booking_id}/cancel_my',
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_my(
    booking_id: int,
    user: UserSchema = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    return await change_booking_status(booking_id, session, user, 'cancelled')


@router.get(
    "/{headset_id}/unavailable",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def get_bookings(
    headset_id: int,
    date: date,
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = datetime.combine(date, datetime.max.time())
    local_time_now = convert_time(datetime.now())

    query = select(
        booking.c.start_time,
        booking.c.end_time
    ).where(
        and_(
            booking.c.headset_id == headset_id,
            booking.c.status.in_(['confirmed', 'pending']),
            booking.c.start_time >= start_of_day,
            booking.c.start_time > local_time_now,
            booking.c.end_time <= end_of_day
        )
    )

    bookings = (await session.execute(query)).fetchall()

    if not bookings:
        return {"result": []}

    result = [BookingTimeSchema.from_orm(booking) for booking in bookings]
    return {"result": result}


@router.post(
    '/book',
    status_code=status.HTTP_201_CREATED,
    response_model=dict
)
async def book(
    booking_request: BookingCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user: UserSchema = Depends(get_current_user)
) -> dict:
    
    query = select(
        booking
    ).where(
        and_(      
            booking.c.headset_id == booking_request.headset_id,
            booking.c.status.in_(['confirmed', 'pending']),
            booking.c.start_time == convert_time(booking_request.start_time),
            booking.c.end_time == convert_time(booking_request.end_time)
        )
    )

    if (await session.execute(query)).fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This time slot is already booked')

    auto_confirm = (await session.execute(select(settings.c.auto_confirm))).fetchone()[0]

    booking_status = 'confirmed' if auto_confirm else 'pending'

    start_time = convert_time(booking_request.start_time)
    end_time = convert_time(booking_request.end_time)
    cost = await get_cost(booking_request.headset_id, session)

    try:
        stmt = insert(booking).values(
            user_id=user.id,
            headset_id=booking_request.headset_id,
            cost=cost,
            start_time=start_time,
            end_time=end_time,
            created_at=convert_time(datetime.now()),
            status=booking_status
        )
        
        await session.execute(stmt)
        await session.commit()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
    
    await send_email(
        booking_status,
        user.email,
        await get_headset_name(booking_request.headset_id, session),
        start_time,
        end_time,
        cost)

    return {'status': booking_status}
