from fastapi import status, HTTPException
from src.models.headsets import headset
from src.models.bookings import booking
from src.models.users import user
from src.schemas.user_schema import UserSchema
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.celery_service import send_email_task


async def get_headset_name(headset_id: int, session: AsyncSession) -> str:
        query = select(headset.c.name).where(headset.c.id == headset_id)
        return (await session.execute(query)).fetchone()[0]


async def get_cost(headset_id: int, session: AsyncSession) -> int:
        query = select(headset.c.cost).where(headset.c.id == headset_id)
        return (await session.execute(query)).fetchone()[0]


async def change_booking_status(booking_id: int, session: AsyncSession, current_user: UserSchema, booking_status: str) -> None:
    query = select(
        booking
    ).where(
        booking.c.id == booking_id,
    )
    my_booking = (await session.execute(query)).fetchone()

    if not my_booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Booking not found')
    if not current_user.is_superuser and my_booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    if my_booking.status == booking_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Booking is already {booking_status}')
    
    stmt = update(
        booking
    ).where(
        booking.c.id == booking_id,
    ).values(
        status=booking_status
    )
    
    await session.execute(stmt)
    await session.commit()
    user_email = (await session.execute(select(user.c.email).where(user.c.id == my_booking.user_id))).fetchone()[0]

    await send_email(
        booking_status,
        user_email,
        await get_headset_name(my_booking.headset_id, session),
        my_booking.start_time,
        my_booking.end_time,
        my_booking.cost
    )

    return


async def send_email(*args) -> None:
    if len(args) == 3:
        email_result = send_email_task.delay(status = args[0], user_email=args[1], headset_name=args[2], cost=args[3], old_cost=args[4])
    else:
        email_result = send_email_task.delay(*args)
    email_result = email_result.get()
    if email_result != 'success':
        raise HTTPException(status_code=500, detail='Error while sending email')
    return
