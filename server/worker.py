import zmq
import pickle
import logging
import time
from sqlalchemy.orm import scoped_session

from config.TEMP_unique_key import TEST_KEY
from config.metadata import serverRequests, clientRequests, commonRequests
from config.exceptions import UnrecognizedClientResponse
from shared.objects.communication import Communication
from shared.methods.hashed_pickle import sign_message, verified_message
from .database.operations.fetch_and_retrieve_link import get_link_from_db, pass_link_to_db, update_link
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
                logging.error("No result found when trying to get link to scrape from database.")
                #TODO add additional field in communication that will explain that link is empty
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
                print(f"XDDDD{status}")
                if status == clientRequests.status_ok:
                    server_log.debug(f"Received data has o.k. status")
                    server_log.info()
                    # Update link so that it won't be used again in scraping process.
                    update_link(active_session,
                                    link_id,
                                    "Link scrapped successfully")
                    # TODO add offer info to offer table
                    pass
                elif status == clientRequests.status_failed:
                    server_log.info(f"Received webpage data has failed status.")
                    fail_reason = additional_variables["fail_reason"]
                    if fail_reason == clientRequests.failed_reason_dead_link:
                        server_log.info(f"Failed status because the link was dead")
                        update_link(active_session,
                                    link_id,
                                    "Link is dead")
                    elif fail_reason == clientRequests.failed_reason_scrape_timeout:
                        server_log.info(f"Failed status because of link timeout")
                        update_link(active_session,
                                    link_id,
                                    "Link failed because of timeout",
                                    set_link_as_scraped=False,
                                    set_currently_being_scraped_status_as_false=False)
                    elif fail_reason == clientRequests.failed_reason_unsupported_page_layout:
                        server_log.info(f"Failed status because the offer page had unsupported layout")
                        update_link(active_session,
                                    link_id,
                                    "Unsupported page layout")
                else:
                    print("yyyyyyyyyy")
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



