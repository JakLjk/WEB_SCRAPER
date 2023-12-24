from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from bs4 import BeautifulSoup

from .scraper_utils import pick_selenium_driver, close_popup
from my_loggers.setup_screenshot import save_screenshot_to_folder_as
from config.client_config import seleniumConfig


def get_link_for_range_price(min_price=0,
                   max_price=100000000, 
                   interval=1000) -> str:
    """Generates link which is limited in scope by page 'price' filter."""
    LINK = """https://www.otomoto.pl/osobowe?search[filter_float_price%3Afrom]={}&search[filter_float_price%3Ato]={}"""
    for i in range(min_price, max_price, interval):
        curr_min = i
        curr_max = i + interval - 1
        yield LINK.format(curr_min, curr_max), curr_min, curr_max


def get_link_for_all_pages_in_range_price(min_price:int,
                                max_price:int, 
                                num_pages:int):
    LINK = """https://www.otomoto.pl/osobowe?search[filter_float_price%3Afrom]={}&search[filter_float_price%3Ato]={}&page={}"""
    for curr_page_num in range(num_pages, 0, -1):
        yield LINK.format(min_price, max_price, curr_page_num), curr_page_num


def get_num_of_pages(driver:WebDriver, link:str):
    driver.get(link)
    close_popup(driver, "onetrust-accept-btn-handler")
    last_page_num = driver.find_elements(By.CSS_SELECTOR,".ooa-g4wbjr.eezyyk50")
    if len(last_page_num) == 0:
        if "brak wyników wyszukiwania" in driver.page_source:
            raise ValueError("No offers available at this scope")
        else:
            return 1
    else:
        last_page = last_page_num[-1].text
        return int(last_page)


def get_offer_links_from_specified_page(driver:WebDriver, link:str) -> list:
    driver.get(link)
    close_popup(driver, "onetrust-accept-btn-handler")
    source = driver.page_source
    
    WebDriverWait(driver, seleniumConfig.page_js_load_time_s).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.e17gkxda1.ooa-1l0bag1.er34gjf0')))

    soup = BeautifulSoup(source, "html.parser")
    link_boxes = soup.find_all("h1", {"class":"e1ajxysh9 ooa-1ed90th er34gjf0"})
    scraped_links = [elem.find("a")["href"] for elem in link_boxes]
    if len(scraped_links) == 0:
        driver.get_screenshot_as_file(save_screenshot_to_folder_as("zero_links_error", "png"))
        raise ValueError(f"Number of returned links is equal 0!")
    return scraped_links

