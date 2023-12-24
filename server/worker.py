import zmq
import pickle
import logging
import time
from sqlalchemy.orm import scoped_session

from config.TEMP_unique_key import TEST_KEY
from config.metadata import serverRequests
from config.metadata import clientRequests
from shared.objects.communication import Communication
from shared.methods.hashed_pickle import sign_message, verified_message
from .database.operations.fetch_and_retrieve_link import get_link_from_db 
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
        server_log.info(f"Received request from client.")

        start_time = time.time()
        message:Communication = verified_message(TEST_KEY, received_data)
        server_log.debug(f"Verifying message took {start_time - time.time()} seconds.")

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
        
        active_session.close()



