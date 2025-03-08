import uuid

from sqlalchemy import Table, Column, String, Boolean, MetaData
from sqlalchemy.dialects.postgresql import UUID


metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_subscribed_to_email", Boolean, default=False, nullable=False)
)
