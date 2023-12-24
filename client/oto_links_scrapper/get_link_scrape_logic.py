from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from .scraper_utils import pick_selenium_driver, close_popup
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
        yield LINK.format(min_price, max_price, curr_page_num)


def get_num_of_pages(link:str):
    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                   seleniumConfig.run_headless)
    driver.get(link)
    close_popup(driver, "onetrust-accept-btn-handler")
    last_page_num = driver.find_elements(By.CSS_SELECTOR,".ooa-g4wbjr.eezyyk50")
    if len(last_page_num) == 0:
        if "brak wyników wyszukiwania" in driver.page_source:
            driver.quit()
            raise ValueError("No offers available at this scope")
        else:
            driver.quit()
            return 1
    else:
        last_page = last_page_num[-1].text
        driver.quit()
        return last_page


def get_offer_links_from_specified_page(link) -> list:
    pass