from selenium.webdriver import Firefox, Chrome, Safari, Edge
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from config.client_config import seleniumConfig

def pick_selenium_driver(browser_type="firefox", headless=True) -> WebDriver:
    "Returns initialised driver based on user preferences"
    browser_type = browser_type.lower()
    accepted_drivers = {
        "firefox":Firefox,
        "chrome":Chrome,
        "safari":Safari,
        "edge":Edge}
    accepted_options = {
        "firefox":FirefoxOptions,
        "chrome":Chrome,
        "safari":Safari,
        "edge":Edge}
    try:
        selected_options = accepted_options[browser_type]()
        if headless == True:
            selected_options.add_argument('--headless')
        selected_driver =  accepted_drivers[browser_type](options=selected_options)
        return selected_driver
    except TypeError:
        return None
    

def close_popup(driver:WebDriver, id_identifier:str):
    privacy_button = (WebDriverWait(driver, seleniumConfig.popup_load_wait_time_s)
                    .until(EC.presence_of_element_located((By.ID, id_identifier))))
    privacy_button.click()
    

