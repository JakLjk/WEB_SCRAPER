from sqlalchemy.orm import scoped_session
from sqlalchemy.dialects.mysql import insert
from .. import links
from config.metadata import dbFieldsDefinitions
from config.server_config import linkFiltering
from config.exceptions import NoScrapeableLinkInDB


def check_if_link_already_in_db(session:scoped_session, provided_link:str):
    return session.query(links).filter(links.c.link==provided_link).first() is not None


def get_link_from_db(session:scoped_session):

    link_row = session.query(links).filter(
        links.c.linkWasScraped==False,
        links.c.linkIsNowBeingScraped==False,
        # Makes sure that the same link won't be scraped twice
        links.c.isDuplicateOfAlreadyExistingLink==False,
        links.c.failedTries < linkFiltering.max_link_fails).first()
    if link_row is None:
        raise NoScrapeableLinkInDB("Trying to get link from DB resulted with 'NoneType' response")
        
    session.query(links).filter(links.c.idL == link_row.idL).update({"linkIsNowBeingScraped":True})
    session.commit()

    return {"link_id":link_row.idL,
            "link":link_row.link}

def pass_link_to_db(session:scoped_session, links_from_client:list):

    data = [{"link":l,
             "isDuplicateOfAlreadyExistingLink": 
                check_if_link_already_in_db(session, l),
             "failedTries":0,
             "linkWasScraped":False,
             "linkIsNowBeingScraped":False,
             "statusDescription":""}
             for l in links_from_client]
    session.execute(insert(links), data)
    session.commit()
    

def update_link(session:scoped_session,
                link_id,
                update_description:str="N/A",
                set_link_as_scraped=True,
                set_currently_being_scraped_status_as_false=True,
                add_1_to_failed_tries=False):
    
    session.query(links).filter(links.c.idL == link_id).update(
        {"linkIsNowBeingScraped":not(set_currently_being_scraped_status_as_false),
         "linkWasScraped":set_link_as_scraped,
         "statusDescription":update_description})
    if add_1_to_failed_tries == True:
        q = session.query(links.c.idL == link_id)
        q.failedTries = links.c.failedTries + 1
    session.commit()
