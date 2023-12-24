

from .scraper_utils import pick_selenium_driver
from config.client_config import seleniumConfig
from config.exceptions import UnsupportedPageLayout

def get_offer_page_raw(link:str):
    # TODO check if oage redirects to carsmile 
    driver = pick_selenium_driver(seleniumConfig.browser_type,
                                  seleniumConfig.run_headless)
    driver.get(link)
    if "carsmile" in driver.current_url:
        raise UnsupportedPageLayout("This link redirects to 'carsmile' webpage, which is not supported")

    return driver.page_source
    


