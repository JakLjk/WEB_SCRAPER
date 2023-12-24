class clientConfig:
    server_ip_port:str = "localhost:4123"

class seleniumConfig:
    run_headless = True
    browser_type = "firefox"
    popup_load_wait_time_s = 5

class linkScraping:
    min_offer_price = 0
    max_offer_price = 99999999
    price_intervals = 1000