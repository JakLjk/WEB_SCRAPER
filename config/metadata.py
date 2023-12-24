class clientRequests:
    get_link = "getLink"


class serverRequests:
    send_link = "sendLink"


class dbFieldsDefinitions:
    class linksTable:
        scrape_status_scraped = "WAS_SCRAPED"
        scrape_status_being_scraped = "IS_NOW_SCRAPED"
        scrape_status_not_scraped = "NOT_SCRAPED"
