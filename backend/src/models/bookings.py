from sqlalchemy import Table, Column, Integer, String, ForeignKey, TIMESTAMP, MetaData
from sqlalchemy.dialects.postgresql import UUID
from src.models.users import user
from src.models.headsets import headset

metadata = MetaData()

booking = Table(
    "booking",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey(user.c.id), nullable=False),
    Column("headset_id", Integer, ForeignKey(headset.c.id), nullable=False),
    Column("cost", Integer, nullable=False),
    Column("start_time", TIMESTAMP, nullable=False),
    Column("end_time", TIMESTAMP, nullable=False),
    Column("created_at", TIMESTAMP, nullable=False),
    Column("status", String, nullable=False)
)
