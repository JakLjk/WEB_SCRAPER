class clientRequests:
    get_link = "getLink"
    pass_link_batch = "passLinkBatch"


class serverRequests:
    send_link = "sendLink"

class commonRequests:
    query_ok = "statusOk"
    query_not_ok = "statusNotOk"


class dbFieldsDefinitions:
    class linksTable:
        scrape_status_scraped = "WAS_SCRAPED"
        scrape_status_being_scraped = "IS_NOW_SCRAPED"
        scrape_status_not_scraped = "NOT_SCRAPED"
