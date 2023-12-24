from sqlalchemy.orm import scoped_session

from .. import links
from config.metadata import dbFieldsDefinitions


def get_link_from_db(session:scoped_session):

    link_row = session.query(links).filter(
        links.c.linkScrapeCurrentStep==dbFieldsDefinitions.linksTable.scrape_status_not_scraped).one()

    session.query(links).filter(links.c.idL == link_row.idL).update({"linkScrapeCurrentStep":
                                                                     dbFieldsDefinitions.linksTable.scrape_status_being_scraped})
    session.commit()

    return {"link_id":link_row.idL,
            "link":link_row.link}

def pass_link_to_db(l):
    pass