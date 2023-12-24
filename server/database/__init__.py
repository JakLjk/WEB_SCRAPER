from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean, DATETIME


meta = MetaData()

# Load database tables metadata on import
links = Table(
    "links",
    meta,
    Column("idL", Integer, autoincrement=True, primary_key=True),
    Column("link", Text),
    Column("linkWasScraped", Boolean),
    Column("linkIsNowScraped", Text),
    Column("linkInsertDate", DATETIME))


