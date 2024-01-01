from sqlalchemy.orm import scoped_session
from sqlalchemy.dialects.mysql import insert

from .. import links, offers, raw_data
from shared.objects.webpage import Webpage
from config.server_config import dbConfig
from config.exceptions import InsertDetailsToDBFailed, InsertEquipmentToDBFailed, InsertMainOfferDataFailed
from .common_operations import currently_available_column_names, add_column, insert_dict_values_to_db


def pass_offer_details_to_db(Session:scoped_session,
                            link_db_entry_id:int,
                            webpage_object:Webpage):

    main_data = [{
        "link":webpage_object.link,
        "idL":link_db_entry_id,
        "title":webpage_object.offer_title,
        "price":webpage_object.price,
        "currency":webpage_object.currency,
        "coordinates":webpage_object.coordinates,
        "description":webpage_object.description}]

    raw_data_list = [{
        "idL":link_db_entry_id,
        "rawData":webpage_object.raw_data}]
    
    # Checking which details columns are already in database and adding the ones that are missing
    # in comparison to the new offer data that is to be uploaded to db
    active_session = Session()
    details_table_name = dbConfig.offer_details_table_name
    details_to_add_to_db = webpage_object.details
    details_to_add_to_db = {replace_space_to_floor(key):val for key, val in details_to_add_to_db.items()}
    details_to_add_to_db = {normalize_column_names(key):val for key, val in details_to_add_to_db.items()}
    detail_names = set(details_to_add_to_db.keys())
    curr_columns = currently_available_column_names(active_session, details_table_name)
    columns_to_add = detail_names - curr_columns
    for column_name in columns_to_add:
        add_column(active_session, details_table_name, column_name, "text")
    details_to_add_to_db["idL"]=link_db_entry_id
    active_session.close()

    # Checking which equipment columns are already in database and adding the ones that are missing
    # in comparison to the new offer data that is to be uploaded to db
    active_session = Session()
    equipment_table_name=dbConfig.offer_equipment_table_name
    equipment=webpage_object.equipment
    # Only if there is equipment to be added
    if equipment:
        equipment=[replace_space_to_floor(eq) for eq in equipment]
        equipment=[normalize_column_names(eq) for eq in equipment]
        equipment_columns = set(equipment)
        equipment_columns_in_db=currently_available_column_names(active_session, equipment_table_name)
        columns_to_add = equipment_columns - equipment_columns_in_db
        for column_name in columns_to_add:
            add_column(active_session, equipment_table_name, column_name, "text")
        equipment_to_add_to_db={eq:True for eq in equipment}
    else:
        equipment_to_add_to_db=None
    active_session.close()
    
    # Creating transaction session so that are inserts are appended together
    with Session() as connection:
        connection.execute(insert(offers), main_data)
        connection.execute(insert(raw_data), raw_data_list)
        insert_dict_values_to_db(connection,
                                link_db_entry_id,
                                details_table_name,
                                details_to_add_to_db,
                                auto_commit=False)
        # Add equipment only if such is available
        if equipment_to_add_to_db:
            insert_dict_values_to_db(connection,
                        link_db_entry_id,
                        equipment_table_name,
                        equipment_to_add_to_db,
                        auto_commit=False)
        connection.commit()


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