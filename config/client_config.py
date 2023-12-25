class clientConfig:
    server_ip_port:str = "localhost:4123"

class seleniumConfig:
    run_headless = False
    browser_type = "firefox"
    wait_before_script = 0.6
    popup_load_wait_time_s = 3
    page_js_load_time_s = 4

class linkScraping:
    min_offer_price = 0
    max_offer_price = 99999999
    price_intervals = 1000