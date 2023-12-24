
import zmq
import logging
import time

import pickle

from config.TEMP_unique_key import TEST_KEY
from config.metadata import clientRequests
from config.client_config import clientConfig, linkScraping
from shared.methods.hashed_pickle import sign_message, verified_message
from shared.objects.communication import Communication
from .oto_links_scrapper.get_link_scrape_logic import link_generator, \
                                                        get_num_of_pages, \
                                                        get_link_for_all_pages_in_range_price, \
                                                        get_offer_links_from_specified_page


main_log = logging.getLogger("MAIN_LOG")
client_log = logging.getLogger("CLIENT_LOG")


def launch_client(work_type:str):
    if work_type == "mineLinks":
        lauch_mine_links()
    elif work_type == "mineOffers":
        launch_mine_offers()


def lauch_mine_links():
    min_price = linkScraping.min_offer_price
    max_price = linkScraping.max_offer_price
    price_interval = linkScraping.price_intervals
    client_log.info(f"Scraping offer links")
    client_log.debug(f"Page filters details: min price: {min_price} | max price: {max_price} | price interval: {price_interval}")
    for link, min_p, max_p in link_generator(min_price, max_price, price_interval):
        client_log.debug(f"Current page link: {link}")
        num_of_pages = get_num_of_pages(link)
        client_log.info(f"There are {num_of_pages} offer pages in price scope {min_p} - {max_p}")
        for link in get_link_for_all_pages_in_range_price(min_p, max_p, num_of_pages):
            link = get_offer_links_from_specified_page(link)



def launch_mine_offers():
    client_log.info(f"Client will try to establish connection with server {clientConfig.server_ip_port}")
    # TODO Check if connection can be established with server
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{clientConfig.server_ip_port}")
    
    # TODO Add arguments when to stop
    # TODO Add timeout feature
    comm = Communication()

    while True:
        # Request a link to scrape
        client_log.info("Requesting link to parse from server")
        comm.set_comm_details(
            command=clientRequests.get_link)
        
        start_time = time.time()
        signed_message = sign_message(TEST_KEY, comm)
        client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")

        client_log.info("Sending request to server...")
        socket.send_json(signed_message)
        client_log.info("Message sent")

        client_log.info("Received data from server")
        received_data = socket.recv_json()
        start_time = time.time()
        message:Communication = verified_message(TEST_KEY, received_data)
        client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")

        print(message.get_data())

        # Do Further Stuff with received link...

        time.sleep(3)
