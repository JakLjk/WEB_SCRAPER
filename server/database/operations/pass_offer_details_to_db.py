from sqlalchemy.orm import scoped_session

from shared.objects.webpage import Webpage
from config.server_config import dbConfig
from .common_operations import currently_available_column_names, add_column, insert_values_to_db

def pass_offer_details_to_db(session:scoped_session,
                            link_db_entry_id:int,
                            webpage_object:Webpage):
    

    # Pass data to main offer table
    main_data = [{
        "link":webpage_object.link,
        "title":webpage_object.offer_title,
        "price":webpage_object.price,
        "currency":webpage_object.currency,
        "coordinates":webpage_object.coordinates,
        "description":webpage_object.description}]
    
    # Pass data to 'raw data table'
    raw_data_table = [{
        "raw_data":webpage_object.raw_data}]

    # Pass data to details table
    table_name=dbConfig.offer_details_table_name
    details = webpage_object.details
    details = {replace_space_to_floor(key):val for key, val in details.items()}
    details = {normalize_column_names(key):val for key, val in details.items()}
    detail_names = set(details.keys())
    curr_columns = currently_available_column_names(session, table_name)
    columns_to_add = detail_names - curr_columns
    
    for column_name in columns_to_add:
        print(f"ADDING COLUMN: {column_name}")
        add_column(session, table_name, column_name, "text")
    details["idL"]=link_db_entry_id
    insert_values_to_db(session,
                        table_name,
                        details)
    
    # Pass data to equiplent table

def replace_space_to_floor(string:str) -> str:
    return string.replace(" ", "_")

def normalize_column_names(col_name:str) -> str:
    REPLACE = {
    # "ą":"a",
    # "ź":"z",
    # "ż":"z",
    # "ł":"l",
    # " ":"_",
    # "ć":"c",
    # "ń":"n",
    # "ś":"s",
    # "ó":"o",
    # "ę":"e",
    "(":"",
    ")":"",
    "-":"_",
    ",":"_",
    "/":"_",
    ".":"_",
    ";":"_",
    ":":"_"
    }
    for old_val, new_val in REPLACE.items():
        col_name = col_name.replace(old_val.lower(), new_val.lower())
    return col_name