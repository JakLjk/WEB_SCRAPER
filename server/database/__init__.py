from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean, DATETIME, TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT


meta = MetaData()

# Load database tables metadata on import
links = Table(
    "links",
    meta,
    Column("idL", Integer, autoincrement=True, primary_key=True),
    Column("isDuplicateOfAlreadyExistingLink", Boolean),
    Column("failedTries", Integer),
    Column("link", Text),
    Column("linkWasScraped", Boolean),
    Column("linkIsNowBeingScraped", Boolean),
    Column("linkInsertDate", TIMESTAMP),
    Column("statusDescription", Text))

raw_data = Table(
    "offer_raw_data",
    meta,
    Column("idO", Integer, autoincrement=True, primary_key=True),
    Column("idL", Integer, ForeignKey("links.idL")),
    Column("offerRawDataInsertDate", TIMESTAMP),
    Column("rawData", LONGTEXT))

offers = Table(
    "offers",
    meta,
    Column("idO", Integer, autoincrement=True, primary_key=True),
    Column("idL", Integer, ForeignKey("links.idL")),
    Column("insertDate", TIMESTAMP),
    Column("link", Text),
    Column("title",Text),
    Column("price", Text),
    Column("currency", Text),
    Column("coordinates", Text),
    Column("description", Text))

