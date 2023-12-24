
import zmq
import logging
import time

import pickle

from config.TEMP_unique_key import TEST_KEY
from config.exceptions import ServerNegativeResponse, UnsupportedPageLayout
from config.metadata import clientRequests, commonRequests
from config.client_config import clientConfig, linkScraping, seleniumConfig
from shared.methods.hashed_pickle import sign_message, verified_message
from shared.objects.communication import Communication
from .oto_links_scrapper.get_link_scrape_logic import get_link_for_range_price, \
                                                        get_num_of_pages, \
                                                        get_link_for_all_pages_in_range_price, \
                                                        get_offer_links_from_specified_page
from .oto_links_scrapper.get_offer_raw_html_logic import get_offer_page_raw
from .oto_links_scrapper.scraper_utils import pick_selenium_driver


main_log = logging.getLogger("MAIN_LOG")
client_log = logging.getLogger("CLIENT_LOG")


def launch_client(work_type:str):
    if work_type == "mineLinks":
        launch_mine_links()
    elif work_type == "mineOffers":
        launch_mine_offers()


def launch_mine_links():
    client_log.info(f"Client will try to establish connection with server {clientConfig.server_ip_port}")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{clientConfig.server_ip_port}")
    comm = Communication()

    min_price = linkScraping.min_offer_price
    max_price = linkScraping.max_offer_price
    price_interval = linkScraping.price_intervals
    client_log.info(f"Scraping offer links")
    client_log.debug(f"Page filters details: min price: {min_price} | max price: {max_price} | price interval: {price_interval}")
    client_log.info(f"Creating driver session for links scrapper.")
    client_log.debug(f"Driver type: {seleniumConfig.browser_type} | Run headless {seleniumConfig.run_headless}")
    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                   seleniumConfig.run_headless)
    for link, min_p, max_p in get_link_for_range_price(min_price, max_price, price_interval):
        client_log.debug(f"Current page link: {link}")
        num_of_pages = get_num_of_pages(driver, link)
        if num_of_pages > 500:
            driver.quit()
            raise ValueError(f"Number of pages on filter {min_p} - {max_p} is too high!")
        client_log.info(f"There are {num_of_pages} offer pages in price scope {min_p} - {max_p}")
        for link, page_num in get_link_for_all_pages_in_range_price(min_p, max_p, num_of_pages):
            client_log.info(f"Scraping page {num_of_pages - page_num + 1} / {num_of_pages} with links in price range {min_p} - {max_p} ")
            links = get_offer_links_from_specified_page(driver, link)
            client_log.info(f"Found {len(links)} links. Passing them to server...")
            comm.set_comm_details(command=clientRequests.pass_link_batch,
                                  data_to_pass=links)
            start_time = time.time()
            signed_message = sign_message(TEST_KEY, comm)
            client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
            socket.send_json(signed_message)
            client_log.info("Message sent")
            received_data = socket.recv_json()
            start_time = time.time()
            message:Communication = verified_message(TEST_KEY, received_data)
            client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
            if message.get_command() == commonRequests.query_not_ok:
                driver.quit()
                raise ServerNegativeResponse(f"Server Returned Negative Statement: {message.get_data}")
            else:
                continue
    driver.quit()


def launch_mine_offers():
    client_log.info(f"Client will try to establish connection with server {clientConfig.server_ip_port}")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{clientConfig.server_ip_port}")

    comm = Communication()

    while True:
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

        link_to_scrape = message.get_data()
        try:
            page_raw = get_offer_page_raw(link_to_scrape)
        except UnsupportedPageLayout as upl:
            client_log.error(f"Script encountered unsupported webpage type when scraping raw data.")
            client_log.info(f"Skipping current link...")
            client_log.debug(f"Link which encountered the issue: {link_to_scrape}")
            client_log.debug(f"{upl}")
            continue

        





        # Do Further Stuff with received link...

        time.sleep(3)
