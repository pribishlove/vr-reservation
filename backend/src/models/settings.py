from sqlalchemy import Table, Column, Boolean, MetaData

metadata = MetaData()

settings = Table(
    "settings",
    metadata,
    Column("auto_confirm", Boolean, default=False, nullable=False)
)
