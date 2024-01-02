import zmq
from time import sleep
import time
import threading
import logging

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


from config.main_config import serverConfig
from .database.launch import get_db_engine
# from .database.dbschema import load_db_schema
from .worker import init_worker_routine

serv_log = logging.getLogger("SERV_LOG")

def launch_server():
    serv_log.info("Initialising database engine")
    engine = get_db_engine()
    serv_log.info("Creating database global Session object")
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    serv_log.info("Database Session initialised")


    serv_log.info(f"Starting server on port {serverConfig.bindPort}")

    server_url = f"tcp://*:{serverConfig.bindPort}"
    workers_url = "inproc://workers"

    context = zmq.Context.instance()

    clients = context.socket(zmq.ROUTER)
    clients.bind(server_url)

    workers = context.socket(zmq.DEALER)
    workers.bind(workers_url)

    from shared.objects.counter import CommonCouter
    c = CommonCouter()

    for i in range(serverConfig.maxThreads): 
        serv_log.debug(f"Initialising thread |{i}|")
        thread = threading.Thread(target=init_worker_routine, args=(workers_url,
                                                                    Session,
                                                                    c))
        thread.daemon = True
        thread.start()
    
    zmq.proxy(clients, workers)

    clients.close()
    workers.close()
    context.term()

