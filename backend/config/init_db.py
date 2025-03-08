from config.database import async_session_maker
from src.auth.utils.create_user import create_admin_user
from src.models.headsets import headset
from src.models.settings import settings
from sqlalchemy import select, insert


async def init_db() -> None:
    await init_headsets_table()
    await create_admin_user()
    await init_settings_table()


async def init_headsets_table() -> None:
    async with async_session_maker() as session:
        if not (await session.execute(select(headset))).fetchone():
            for num in range(1, 4):
                try:
                    stmt = insert(headset).values(
                        name=f'headset{num}',
                        cost=1000
                    )
                    
                    await session.execute(stmt)
                    await session.commit()

                except Exception:
                    print('Error while filling headsets table')


async def init_settings_table() -> None:
    async with async_session_maker() as session:
        if not (await session.execute(select(settings))).fetchone():
            try:
                stmt = insert(settings).values(
                    auto_confirm=False
                )
                
                await session.execute(stmt)
                await session.commit()

            except Exception:
                print('Error while filling settings table')