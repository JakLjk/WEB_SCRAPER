import zmq
import pickle
import logging
import time
from sqlalchemy.orm import scoped_session

from config.TEMP_unique_key import TEST_KEY
from config.metadata import serverRequests, clientRequests, commonRequests
from config.exceptions import UnrecognizedClientResponse, NoScrapeableLinkInDB
from shared.objects.communication import Communication
from shared.objects.webpage import Webpage
from shared.methods.hashed_pickle import sign_message, verified_message
from .database.operations.fetch_and_retrieve_link import get_link_from_db, pass_link_to_db, update_link
from .database.operations.pass_offer_details_to_db import pass_offer_details_to_db
from sqlalchemy.exc import NoResultFound

server_log = logging.getLogger("SERV_LOG")

def init_worker_routine(workers_url:str, 
                        Session:scoped_session,
                        context: zmq.Context = None):
    
    context = context or zmq.Context.instance()

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)
    socket.connect(workers_url)
    
    active_session = Session()

    comm = Communication()

    while True:
        received_data = socket.recv_json()
        server_log.info(f"Received new message from client")

        start_time = time.time()
        message:Communication = verified_message(TEST_KEY, received_data)
        server_log.debug(f"Verifying message took {round(start_time - time.time(), 4)} seconds.")
        requested_command = message.get_command()

        if requested_command == clientRequests.get_link:
            server_log.info(f"Client is requesting link from database")
            server_log.info(f"Fetching link from database")
            try: 
                link = get_link_from_db(active_session)
            except NoResultFound:
                server_log.error("No result found when trying to get link to scrape from database.")
                link = None
            except NoScrapeableLinkInDB:
                server_log.error("There is no link to be scraped in db.")
                server_log.info("Returning None link")
                link = None
            server_log.info("Passing information back to client")
            comm.set_comm_details(command=serverRequests.send_link,
                                  data_to_pass=link)
            signed_message=sign_message(TEST_KEY, comm)
            socket.send_json(signed_message)

        elif requested_command == clientRequests.pass_link_batch:
            server_log.info("Client is passing link batch")
            server_log.info(f"Passing {len(message.get_data())} links to the database")
            pass_link_to_db(active_session, message.get_data())
            comm.set_comm_details(commonRequests.query_ok)
            signed_message=sign_message(TEST_KEY, comm)
            socket.send_json(signed_message)

        elif requested_command == clientRequests.push_scraped_link_to_server:
            comm = Communication()
            try:
                server_log.info("Client is passing information about scraping procedure.")
                server_log.debug("unwrapping received information...")
                status = message.get_status()
                # data = message.get_data()
                additional_variables = message.get_additional_variables()
                link_id = additional_variables["link_id"]
                if status == clientRequests.status_ok:
                    server_log.info(f"Received webpage data that has o.k. status")
                    server_log.debug(f"Unwrapping received message's data")
                    webpage:Webpage = message.get_data()
                    print(webpage)
                    # Update link so that it won't be used again in scraping process.
                    server_log.info("Updating link table with information about link's scraping process")
                    update_link(active_session,
                                    link_id,
                                    "Link scrapped successfully")
                    server_log.info(f"Link status updated")
                    server_log.info("Appeding offer to offer's tables:")
                    try:
                        pass_offer_details_to_db(session=active_session,
                                                 link_db_entry_id=link_id,
                                                 webpage_object=webpage)
                    except Exception as ex:
                        raise ex
                        # TODO 
                        server_log.warning(f"Adding offer to offer's table failed - updating link to previous status [with +1 failed].")
                    # TODO add offer info to offer table
                elif status == clientRequests.status_failed:
                    server_log.info(f"Received webpage data thath has failed status.")
                    fail_reason = additional_variables["fail_reason"]
                    if fail_reason == clientRequests.failed_reason_dead_link:
                        server_log.info(f"Failed status because the link was dead")
                        server_log.debug(f"Link ID: {link_id}")
                        update_link(active_session,
                                    link_id,
                                    "Link is dead")
                    elif fail_reason == clientRequests.failed_reason_scrape_timeout:
                        server_log.info(f"Failed status because of link timeout")
                        update_link(active_session,
                                    link_id,
                                    "Link failed because of timeout",
                                    set_link_as_scraped=False,
                                    set_currently_being_scraped_status_as_false=False,
                                    add_1_to_failed_tries=True)
                    elif fail_reason == clientRequests.failed_reason_unsupported_page_layout:
                        server_log.info(f"Failed status because the offer page had unsupported layout")
                        update_link(active_session,
                                    link_id,
                                    "Unsupported page layout")
                else:
                    raise UnrecognizedClientResponse(f"Response received from client with status: '{status}' is not a proper response!")
                
            except Exception as ex:
                server_log.error(f"There was error during the data - insertion process - sending information to client. ")
                comm = Communication()
                comm.set_comm_details(commonRequests.query_not_ok,
                                      additional_variables={"response_details":str(ex)})
                start_time = time.time()
                signed_message = sign_message(TEST_KEY, comm)
                server_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
                server_log.info("Sending message to client...")
                socket.send_json(signed_message)
                server_log.info("Message sent")
                raise ex
            
            server_log.info(f"Sending feedback information to server")
            comm = Communication()
            comm.set_comm_details(commonRequests.query_ok)
            start_time = time.time()
            signed_message = sign_message(TEST_KEY, comm)
            server_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
            server_log.info("Sending message to client...")
            socket.send_json(signed_message)
            server_log.info("Message sent")

        active_session.close()



