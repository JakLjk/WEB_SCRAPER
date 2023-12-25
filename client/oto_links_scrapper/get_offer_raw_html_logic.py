from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep

from .scraper_utils import pick_selenium_driver
from config.client_config import seleniumConfig
from config.exceptions import UnsupportedPageLayout, DeadOfferLink, NoMapElementLoaded
from .scraper_utils import close_popup

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
    (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
    .until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.ooa-3zf69b.er34gjf0'))))

    # Script which will scroll to map box in order to load it properly
    class_name = 'ooa-yd8sa2'
    script = f"var elements = document.getElementsByClassName('{class_name}'); if (elements.length > 0) elements[0].scrollIntoView();"
    sleep(seleniumConfig.wait_before_script)
    driver.execute_script(script)
    sleep(seleniumConfig.wait_before_script)
    driver.execute_script(script)

    try: 
        #Wait until map box is present
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '.gm-style'))))
    except TimeoutException:
        # Try once more if map box did not load the first time
        sleep(seleniumConfig.wait_before_script*5)
        driver.execute_script(script)
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '.gm-style'))))
        return NoMapElementLoaded
    try:
        # Check if element within map box containing coordinates loaded completely
        (WebDriverWait(driver, seleniumConfig.page_js_load_time_s*5)
        .until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'a[href*="https://maps.google.com/maps?ll="]'))))
    except TimeoutException:
        return NoMapElementLoaded
    return driver.page_source
    
    

    

