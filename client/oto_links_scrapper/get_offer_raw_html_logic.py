from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from time import sleep

from .scraper_utils import pick_selenium_driver
from config.client_config import seleniumConfig
from config.exceptions import UnsupportedPageLayout, DeadOfferLink, NoMapElementLoaded
from .scraper_utils import close_popup

client_log = logging.getLogger("CLIENT_LOG")


def get_offer_page_raw(driver, link:str):
    driver.get(link)
    close_popup(driver, "onetrust-accept-btn-handler")
    # If loaded page redirects to 'carsmile', then raise Exception
    if "carsmile" in driver.current_url:
        raise UnsupportedPageLayout("This link redirects to 'carsmile' webpage, which is not supported")
    try:
        # If element was found, then link is dead:
        element_by_css = driver.find_element(By.CSS_SELECTOR, '.ooa-wgyq1y.er34gjf0')
        raise DeadOfferLink("This link was removed from otomoto webpage")
    except NoSuchElementException:
        pass
    
    # Wating for webpage JS to load completely
    client_log.debug(f"Waiting {seleniumConfig.page_js_load_time_s}s for webpage js to load completely")
    (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
    .until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.ooa-3zf69b.er34gjf0'))))

    # Script which will scroll to map box in order to load it properly
    client_log.debug("Launching script which will scroll down to load webpage completely")
    class_name = 'ooa-yd8sa2'
    script = f"var elements = document.getElementsByClassName('{class_name}'); if (elements.length > 0) elements[0].scrollIntoView();"
    client_log.debug(f"Waiting {seleniumConfig.wait_before_script}s ...")
    sleep(seleniumConfig.wait_before_script)
    client_log.debug(f"Scrolling down.")
    driver.execute_script(script)
    client_log.debug(f"Waiting {seleniumConfig.wait_before_script}s ...")    
    sleep(seleniumConfig.wait_before_script)
    client_log.debug(f"Scrolling down.")
    driver.execute_script(script)

    try: 
        #Wait until map box is present
        client_log.debug(f"Waiting {seleniumConfig.page_js_load_time_s}s for map box to appear...")
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '.gm-style'))))
    except TimeoutException as te:
        # Try once more if map box did not load the first time
        client_log.debug(f"The map box did not appear on time, waiting additional {seleniumConfig.page_js_load_time_s}s")
        longer_wait = seleniumConfig.wait_before_script * 5 
        client_log.debug(f"Waiting {longer_wait}s ...")
        sleep(longer_wait)
        client_log.debug(f"Scrolling down.")
        driver.execute_script(script)
        client_log.debug(f"Waiting...")
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '.gm-style'))))
        client_log.debug(f"Map box appeared during")
    try:
        # Check if element within map box containing coordinates loaded completely
        client_log.debug(f"Checking if element containing link is present within the map box.")
        searched_elem = 'a[href*="https://maps.google.com/maps?ll="]'
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s*5)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, searched_elem))))
    except TimeoutException as te:
        client_log.debug(f"Element {searched_elem} was not present - Timeout Exception triggered")
        raise te
    return driver.page_source
    
    

    

