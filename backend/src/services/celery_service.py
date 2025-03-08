from pydantic import EmailStr
from celery import Celery, current_app
from celery.signals import worker_ready
from celery.schedules import crontab
from datetime import datetime, timedelta
from src.utils.convert_time import convert_time
from src.services.email_service import EmailService
from src.models.bookings import booking
from sqlalchemy import select, and_, update
from config.config import REDIS_PORT
from config.database import async_session_maker
import asyncio


celery = Celery('task', broker=f'redis://redis:{REDIS_PORT}/0', result_backend=f'redis://redis:{REDIS_PORT}/0')

celery.conf.beat_schedule = {
    'cancel-pending-bookings-every-hour': {
        'task': 'src.services.celery_service.cancel_expired_pending_bookings',
        'schedule': crontab(minute=0, hour='*'),
    },
}

@celery.task
def send_email_task(
    status: str,
    user_email: EmailStr,
    headset_name: str,
    start_time: datetime,
    end_time: datetime,
    cost: int | None = None,
    old_cost: int | None = None,
) -> str:
    try:
        if status == 'confirmed':
            EmailService.send_confirm_email(user_email, headset_name, start_time, end_time, cost)
        elif status == 'pending':
            EmailService.send_pendign_email(user_email, headset_name, start_time, end_time, cost)
        elif status == 'cancelled':
            EmailService.send_cancel_email(user_email, headset_name, start_time, end_time)
        elif status == 'notice':
            EmailService.send_notice_email(user_email, headset_name, old_cost, cost)
        return 'success'
    except Exception as e:
        print(e)
        return str(e)


@celery.task
def cancel_expired_pending_bookings():
    asyncio.run(cancel_expired_pending_bookings_async())


async def cancel_expired_pending_bookings_async():
    async with async_session_maker() as session:
        delta_time =  convert_time(datetime.now()) - timedelta(hours=1)
        
        query = select(booking).where(
            and_(
                booking.c.status == 'pending',
                booking.c.created_at < delta_time
            )
        )

        pending_bookings = (await session.execute(query)).fetchall()

        for pending_booking in pending_bookings:
            await session.execute(
                update(booking)
                .where(booking.c.id == pending_booking.id)
                .values(status='cancelled')
            )

        await session.commit()
        return {'status': True}
