from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

headset = Table(
    "headset",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("cost", Integer, nullable=False)
)
