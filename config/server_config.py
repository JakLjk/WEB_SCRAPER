
class dbConfig:
    db_host="192.168.0.226:3306"
    db_name="otomoto_db"
    db_username="root"
    db_password="casaos"

    offer_details_table_name="offer_details"
    offer_equipment_table_name="offer_equipment"
    offer_raw_data_table_name="offer_raw_data"


class linkFiltering:
    # How many times can link fail the scraping process before being thrown away as broken
    max_link_fails=3

