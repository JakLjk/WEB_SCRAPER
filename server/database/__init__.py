from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean, DATETIME
from sqlalchemy.dialects.mysql import LONGTEXT


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

offers = Table(
    "offers",
    meta,
    Column("idO", Integer, autoincrement=True, primary_key=True),
    Column("insertDate", DATETIME),
    Column("link", Text),
    Column("rawHTML", LONGTEXT),
    Column("title",Text),
    Column("price", Text),
    Column("currency", Text),
    Column("coordinates", Text),
    Column("description", Text))

# offer_details = Table(
#     "offer_details",
#     meta,
#     Column("idOD", Integer, autoincrement=True, primary_key=True)
#     Column("")
# )
