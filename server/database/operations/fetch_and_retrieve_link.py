from sqlalchemy.orm import scoped_session
from sqlalchemy.dialects.mysql import insert
from .. import links
from config.metadata import dbFieldsDefinitions


def get_link_from_db(session:scoped_session):

    link_row = session.query(links).filter(
        links.c.linkWasScraped==False,
        links.c.linkIsNowScraped==False).one()

    session.query(links).filter(links.c.idL == link_row.idL).update({"linkIsNowScraped":True})
    session.commit()

    return {"link_id":link_row.idL,
            "link":link_row.link}

def pass_link_to_db(session:scoped_session, links_from_client:list):
    data = [{"link":l,
             "linkWasScraped":False,
             "linkIsNowScraped":False}
             for l in links_from_client]
    session.execute(insert(links), data)
    session.commit()
    
