from sqlalchemy.orm import scoped_session
from sqlalchemy.dialects.mysql import insert
from .. import links
from config.metadata import dbFieldsDefinitions
from config.server_config import linkFiltering


def get_link_from_db(session:scoped_session):

    link_row = session.query(links).filter(
        links.c.linkWasScraped==False,
        links.c.linkIsNowBeingScraped==False,
        links.c.failedTries < linkFiltering.max_link_fails).first()

    session.query(links).filter(links.c.idL == link_row.idL).update({"linkIsNowBeingScraped":True})
    session.commit()

    return {"link_id":link_row.idL,
            "link":link_row.link}

def pass_link_to_db(session:scoped_session, links_from_client:list):
    data = [{"link":l,
             "failedTries":0,
             "linkWasScraped":False,
             "linkIsNowBeingScraped":False}
             for l in links_from_client]
    session.execute(insert(links), data)
    session.commit()
    

def update_link(session:scoped_session,
                link_id,
                update_description:str="N/A",
                set_link_as_scraped=True,
                set_currently_being_scraped_status_as_false=True,
                # TODO
                add_1_to_failed_tries=True):
    
    session.query(links).filter(links.c.idL == link_id).update(
        {"linkIsNowBeingScraped":not(set_currently_being_scraped_status_as_false),
         "linkWasScraped":set_link_as_scraped,
         "statusDescription":update_description})
    session.commit()