import zmq
import logging
import time
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.TEMP_unique_key import TEST_KEY
from config.exceptions import ServerNegativeResponse, UnsupportedPageLayout, \
    DeadOfferLink, NoMapElementLoaded, ServerResponseError, NoResponseFromServer, \
    UnrecognizedServerResponse, UnresolvedWebpageTimeout
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


def launch_client(work_type:str,
                start_from_price_boundary: int | None = None,
                end_on_price_boundary:int | None = None):
    if work_type == "mineLinks":
        launch_mine_links(start_from_price_boundary,
                          end_on_price_boundary)
    elif work_type == "mineOffers":
        launch_mine_offers()


def launch_mine_links(start_from_price_boundary: int | None = None,
                      end_on_price_boundary:int | None = None):
    client_log.info(f"Client will try to establish connection with server {clientConfig.server_ip_port}")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{clientConfig.server_ip_port}")
    comm = Communication()


    min_price = linkScraping.min_offer_price
    max_price = linkScraping.max_offer_price
    price_interval = linkScraping.price_intervals
    if start_from_price_boundary:
        min_price = int(start_from_price_boundary)
    if end_on_price_boundary:
        max_price = int(end_on_price_boundary)
    client_log.info(f"Scraping offer links")
    client_log.debug(f"Page filters details: min price: {min_price} | max price: {max_price} | price interval: {price_interval}")
    client_log.info(f"Creating driver session for links scrapper.")
    client_log.debug(f"Driver type: {seleniumConfig.browser_type} | Run headless {seleniumConfig.run_headless}")
    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                   seleniumConfig.run_headless)
    for link, min_p, max_p in get_link_for_range_price(min_price, max_price, price_interval):
        client_log.debug(f"Current page link: {link}")
        negative_webpage_response = True
        retry = 0
        timeout_retries = seleniumConfig.timeout_exception_max_retries
        timeout_wait = seleniumConfig.timeout_exception_retry_time_s
        while negative_webpage_response:
            try:
                num_of_pages = get_num_of_pages(driver, link)
                negative_webpage_response = False
            except TimeoutException:
                client_log.exception("Timeout exception while trying to load webpage with links list")
                retry +=1
                if retry > timeout_retries: 
                    raise UnresolvedWebpageTimeout(f"Could not establish proper webpage connection after {timeout_retries} retries")
                client_log.error("Retrying...")
                time.sleep(timeout_wait)
                continue
        if num_of_pages > 500:
            driver.quit()
            raise ValueError(f"Number of pages on filter {min_p} - {max_p} is too high!")
        client_log.info(f"There are {num_of_pages} offer pages in price scope {min_p} - {max_p}")

        for link, page_num in get_link_for_all_pages_in_range_price(min_p, max_p, num_of_pages):
            client_log.info(f"Scraping page {num_of_pages - page_num + 1} / {num_of_pages} with links in price range {min_p} - {max_p} ")
        negative_webpage_response = True
        retry = 0
        while negative_webpage_response:
            try:
                links = get_offer_links_from_specified_page(driver, link)
                negative_webpage_response = False

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
                
            except TimeoutException:
                client_log.exception("Timeout exception while trying to load webpage with links list")
                retry +=1
                if retry > timeout_retries: 
                    raise UnresolvedWebpageTimeout(f"Could not establish proper webpage connection after {timeout_retries} retries")
                client_log.error("Retrying...")
                time.sleep(timeout_wait)
                continue
            

    driver.quit()





def launch_mine_offers():
    client_log.info(f"Client will try to establish connection with server {clientConfig.server_ip_port}")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{clientConfig.server_ip_port}")
    comm = Communication()
    

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
            
            received_data = socket.recv_json()
            client_log.info("Received data from server")
            client_log.debug("Verifying message...")
            start_time = time.time()
            message:Communication = verified_message(TEST_KEY, received_data)
            client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")

            client_log.info("Unwrapping message data")
            message = message.get_data()
            if message == None:
                client_log.error(f"Server returned None as link, requesting new link in {clientConfig.wait_time_for_new_link_s} seconds ")
                time.sleep(clientConfig.wait_time_for_new_link_s)
                continue
            link_id = message["link_id"]
            link_to_scrape = message["link"]
            client_log.debug(f"Link to scrape: {link_to_scrape}")
            negative_webpage_response = True
            retry = 0
            timeout_retries = seleniumConfig.timeout_exception_max_retries
            timeout_wait = seleniumConfig.timeout_exception_retry_time_s
            while negative_webpage_response:
                try:
                    client_log.info("Fetching webpage raw data")
                    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                seleniumConfig.run_headless)
                    page_raw = get_offer_page_raw(driver, link_to_scrape)

                    negative_webpage_response = False
                except UnsupportedPageLayout as upl:
                    driver.quit()
                    client_log.error(f"Script encountered unsupported webpage type when scraping raw data.")
                    client_log.info(f"Skipping current link...")
                    client_log.debug(f"Link which encountered the issue: [{link_to_scrape}]")
                    client_log.debug(f"{upl}")
                    comm.set_comm_details(
                        clientRequests.push_scraped_link_to_server,
                        clientRequests.status_failed,
                        None,
                        {"link_id":link_id,
                        "fail_reason":clientRequests.failed_reason_unsupported_page_layout})
                    client_log.info(f"Passing information to server about failed scraping...")
                    start_time = time.time()
                    signed_message = sign_message(TEST_KEY, comm)
                    client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
                    socket.send_json(signed_message)
                    client_log.info(f"Server notified.")
                    client_log.info(f"Proceeding to scrape next link...")
                    # ########################
                    client_log.info(f"Waiting for response...")
                    # waiting for feedback from server to see if the offer data was properly inserted into database
                    received_data = socket.recv_json()
                    client_log.info(f"Received message from server")
                    start_time = time.time()
                    message:Communication = verified_message(TEST_KEY, received_data)
                    client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
                    # Check what kind of response did server send back to see if the offer data was properly 
                    # inserted into the database
                    if message.get_command() == commonRequests.query_not_ok:
                        error_message = message.get_additional_variables()["response_details"]
                        raise ServerResponseError(f"Server returned negative response: ''{error_message}''")
                    elif message.get_command() == commonRequests.query_ok:
                        client_log.info("Server returned 'o.k.' status for offer's database insertion.")
                        negative_webpage_response = False
                        continue
                    else:
                        raise UnrecognizedServerResponse("Server did not respond in a defined way.") 
                    # ########################
                    continue
                except DeadOfferLink:
                    path = save_screenshot_to_folder_as(f"dead_link_{link_id}_", "png")
                    driver.get_screenshot_as_file(path)
                    driver.quit()
                    client_log.warning(f"Current link is dead (offer was probably removed from webpage)")
                    client_log.warning(f"Screenshot of this page can be found here: [{path}]")
                    client_log.debug(f"Link ID: {link_id}")
                    comm.set_comm_details(
                        clientRequests.push_scraped_link_to_server,
                        clientRequests.status_failed,
                        None,
                        {"link_id":link_id,
                        "fail_reason":clientRequests.failed_reason_dead_link})
                    client_log.info(f"Passing information to server about failed scraping...")
                    start_time = time.time()
                    signed_message = sign_message(TEST_KEY, comm)
                    client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
                    socket.send_json(signed_message)
                    client_log.info(f"Server notified.")
                    client_log.info(f"Proceeding to scrape next link...")
                    # ########################
                    client_log.info(f"Waiting for response...")
                    # waiting for feedback from server to see if the offer data was properly inserted into database
                    received_data = socket.recv_json()
                    client_log.info(f"Received message from server")
                    start_time = time.time()
                    message:Communication = verified_message(TEST_KEY, received_data)
                    client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
                    # Check what kind of response did server send back to see if the offer data was properly 
                    # inserted into the database
                    if message.get_command() == commonRequests.query_not_ok:
                        error_message = message.get_additional_variables()["response_details"]
                        raise ServerResponseError(f"Server returned negative response: ''{error_message}''")
                    elif message.get_command() == commonRequests.query_ok:
                        client_log.info("Server returned 'o.k.' status for offer's database insertion.")
                        negative_webpage_response = False
                        continue
                    else:
                        raise UnrecognizedServerResponse("Server did not respond in defined way.") 
                    # ########################
                    continue
                except TimeoutException:
                    path = save_screenshot_to_folder_as("timeout_when_fetching_offer_raw", "png")
                    driver.get_screenshot_as_file(path)
                    client_log.exception(F"Failed to load offer page. Print Screen: [{path}]")
                    
                    driver.quit()

                    client_log.error(f"Caught Webdriver exception: {wde}")
                    driver.quit()
                    retry += 1 
                    if retry > timeout_retries:
                        client_log.info("Passing information to server about unsuccessful scraping attempt")
                        comm.set_comm_details(
                        clientRequests.push_scraped_link_to_server,
                        clientRequests.status_failed,
                        None,
                        {"link_id":link_id,
                        "fail_reason":clientRequests.failed_reason_scrape_timeout})
                        client_log.info(f"Passing information to server about failed scraping...")
                        start_time = time.time()
                        signed_message = sign_message(TEST_KEY, comm)
                        client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
                        socket.send_json(signed_message)
                        client_log.info(f"Server notified.")
                        # ########################
                        client_log.info(f"Waiting for response...")
                        # waiting for feedback from server to see if the offer data was properly inserted into database
                        received_data = socket.recv_json()
                        client_log.info(f"Received message from server")
                        start_time = time.time()
                        message:Communication = verified_message(TEST_KEY, received_data)
                        client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
                        # Check what kind of response did server send back to see if the offer data was properly 
                        # inserted into the database
                        if message.get_command() == commonRequests.query_not_ok:
                            error_message = message.get_additional_variables()["response_details"]
                            raise ServerResponseError(f"Server returned negative response: ''{error_message}''")
                        elif message.get_command() == commonRequests.query_ok:
                            client_log.info("Server returned 'o.k.' status for offer's database insertion.")
                            negative_webpage_response = False
                            continue
                        else:
                            raise UnrecognizedServerResponse("Server did not respond in defined way.") 
                    client_log.error("Webdriver exception forced script to retry....")
                    time.sleep(timeout_wait)
                    continue   
                    # raise UnresolvedWebpageTimeout(f"Could not get proper webpage connection on offer {link_to_scrape} despite {retry} retires")]
                
                    # client_log.error("Webdriver exception forced script to retry....")
                    # time.sleep(timeout_wait)
                    # continue                    
                    # comm.set_comm_details(
                    #     clientRequests.push_scraped_link_to_server,
                    #     clientRequests.status_failed,
                    #     None,
                    #     {"link_id":link_id,
                    #     "fail_reason":clientRequests.failed_reason_scrape_timeout})
                    # client_log.info(f"Passing information to server about failed scraping...")
                    # start_time = time.time()
                    # signed_message = sign_message(TEST_KEY, comm)
                    # client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
                    # socket.send_json(signed_message)
                    # client_log.info(f"Server notified.")
                    # # ########################
                    # client_log.info(f"Waiting for response...")
                    # # waiting for feedback from server to see if the offer data was properly inserted into database
                    # received_data = socket.recv_json()
                    # client_log.info(f"Received message from server")
                    # start_time = time.time()
                    # message:Communication = verified_message(TEST_KEY, received_data)
                    # client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
                    # # Check what kind of response did server send back to see if the offer data was properly 
                    # # inserted into the database
                    # if message.get_command() == commonRequests.query_not_ok:
                    #     error_message = message.get_additional_variables()["response_details"]
                    #     raise ServerResponseError(f"Server returned negative response: ''{error_message}''")
                    # elif message.get_command() == commonRequests.query_ok:
                    #     client_log.info("Server returned 'o.k.' status for offer's database insertion.")
                    #     continue
                    # else:
                    #     raise UnrecognizedServerResponse("Server did not respond in defined way.") 
                
                # except TimeoutException as te:
                #     path = save_screenshot_to_folder_as("timeout_when_fetching_offer_raw", "png")
                #     driver.get_screenshot_as_file(path)
                #     client_log.exception(F"Failed to load offer page. Print Screen: [{path}]")
                #     driver.quit()
                
                except WebDriverException as wde:
                    client_log.error(f"Caught Webdriver exception: {wde}")
                    driver.quit()
                    retry += 1 
                    if retry > timeout_retries:
                        raise UnresolvedWebpageTimeout(f"Could not get proper webpage connection on offer {link_to_scrape} despite {retry} retires")
                    client_log.error("Webdriver exception forced script to retry....")
                    time.sleep(timeout_wait)
                    continue    





            client_log.info("Creating Webpage object")
            webpage = Webpage(link=link_to_scrape)
            webpage.raw_data = page_raw
            client_log.info("Parsing raw page HTML into proper data scheme")
            # Save last page raw html to see what went wrong if code crashes
            save_raw("raw_1", page_raw)
            # scrape offer details from the raw data 
            get_offer_details(webpage, page_raw)
            # print object in terminal to see some general information about this specific pffer
            print(webpage)
            client_log.debug(f"Creating message for server...")
            # creating message with status ok (if script went to this place 
            # that meants there were no exceptions during scraping process)
            comm.set_comm_details(
                clientRequests.push_scraped_link_to_server,
                clientRequests.status_ok,
                webpage,
                {"link_id":link_id})
            start_time = time.time()
            signed_message = sign_message(TEST_KEY, comm)
            client_log.debug(f"Signing message took {round(time.time() - start_time, 4)} seconds.")
            client_log.info(f"Sending message to server...")
            # sending message to server containing the offer information
            socket.send_json(signed_message)
            client_log.info(f"Message sent")
            client_log.info(f"Waiting for response...")
            # waiting for feedback from server to see if the offer data was properly inserted into database
            received_data = socket.recv_json()
            client_log.info(f"Received message from server")
            start_time = time.time()
            message:Communication = verified_message(TEST_KEY, received_data)
            client_log.debug(f"Verifying message took {round(time.time() - start_time, 4)} seconds.")
            # Check what kind of response did server send back to see if the offer data was properly 
            # inserted into the database
            if message.get_command() == commonRequests.query_not_ok:
                error_message = message.get_additional_variables()["response_details"]
                raise ServerResponseError(f"Server returned negative response: ''{error_message}''")
            elif message.get_command() == commonRequests.query_ok:
                client_log.info("Server returned 'o.k.' status for offer's database insertion.")
                continue
            else:
                raise UnrecognizedServerResponse("Server did not respond in defined way.") 
        except Exception as e:
            client_log.critical(f"There was unidentified exception during script runtime - quitting.")
            driver.quit()
            raise e
        
client_log.info("Script has finished working")
        
