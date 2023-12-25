import zmq
import logging
import time
from selenium.common.exceptions import TimeoutException

from config.TEMP_unique_key import TEST_KEY
from config.exceptions import ServerNegativeResponse, UnsupportedPageLayout, DeadOfferLink
from config.metadata import clientRequests, commonRequests
from config.client_config import clientConfig, linkScraping, seleniumConfig
from my_loggers.setup_screenshot import save_screenshot_to_folder_as
from my_loggers.save_raw_txt import save_raw
from shared.methods.hashed_pickle import sign_message, verified_message
from shared.objects.communication import Communication
from shared.objects.webpage import Webpage
from .oto_links_scrapper.get_link_scrape_logic import get_link_for_range_price, \
                                                        get_num_of_pages, \
                                                        get_link_for_all_pages_in_range_price, \
                                                        get_offer_links_from_specified_page
from .oto_links_scrapper.get_offer_raw_html_logic import get_offer_page_raw
from .oto_links_scrapper.scraper_utils import pick_selenium_driver
from .oto_links_scrapper.parse_raw_offer_html import get_offer_details


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
    
    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                seleniumConfig.run_headless)
    while True:
        try:
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

            client_log.info("Unwrapping message data")
            message = message.get_data()
            link_id = message["link_id"]
            link_to_scrape = message["link"]
            client_log.debug(f"Link to scrape: {link_to_scrape}")
            try:
                client_log.info("Fetching webpage raw data")
                page_raw = get_offer_page_raw(driver, link_to_scrape)
            except UnsupportedPageLayout as upl:
                client_log.error(f"Script encountered unsupported webpage type when scraping raw data.")
                client_log.info(f"Skipping current link...")
                client_log.debug(f"Link which encountered the issue: {link_to_scrape}")
                client_log.debug(f"{upl}")
                continue
            except TimeoutException as te:
                client_log.exception(F"Failed to load offer page - saving print screen with details")
                driver.get_screenshot_as_file(save_screenshot_to_folder_as("timeout_when_fetching_offer_raw", "png"))
                driver.quit()
                raise te
            client_log.info("Creating Webpage object")
            webpage = Webpage(link=link_to_scrape)
            webpage.raw_data = page_raw
            client_log.info("Parsing raw page HTML into proper data scheme")
            # Save last page raw html to see what went wrong if code crashes
            save_raw("raw_1", page_raw)
            try:
                get_offer_details(webpage, page_raw)
            except DeadOfferLink:
                path = save_screenshot_to_folder_as("dead_link", "png")
                driver.get_screenshot_as_file(path)
                client_log.warning(f"Current link is dead (offer was probably removed from webpage)")
                client_log.warning(f"Screenshot of this page can be found here: {path}")
                continue
            print(webpage)
        except Exception as e:
            client_log.critical(f"There was unidentified exception during script runtime - quitting.")
            driver.quit()
            raise e
    driver.quit()

        
