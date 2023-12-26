class clientRequests:
    get_link = "getLink"
    pass_link_batch = "passLinkBatch"
    push_scraped_link_to_server = "pushLink"

    status_ok = "statusOK"
    status_failed = "statusFailed"

    failed_reason_unsupported_page_layout = "failUnsupportedPageLayout"
    failed_reason_dead_link = "failedDeadLink"
    failed_reason_scrape_timeout = "failedScrapeTimeout"


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
