from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from src.models.headsets import headset
from src.schemas.headset_schema import HeadsetSchema
from sqlalchemy import select


router = APIRouter()


@router.get(
    "/headsets",
    status_code=status.HTTP_200_OK,
    response_model=dict
)
async def get_headsets(
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    headsets = (await session.execute(select(headset))).fetchall()
    if not headsets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No headsets found")
    
    result = [HeadsetSchema.from_orm(headset) for headset in headsets]
    return {"result": result}
