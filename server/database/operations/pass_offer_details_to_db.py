from sqlalchemy.orm import scoped_session
from sqlalchemy.dialects.mysql import insert

from .. import links, offers
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
    

    
    with Session() as connection:

        connection.execute(insert(offers), main_data)
        connection.commit()
        print("END-------")


    # try:
    # # Pass data to main offer table
    #     main_data = [{
    #         "link":webpage_object.link,
    #         "title":webpage_object.offer_title,
    #         "price":webpage_object.price,
    #         "currency":webpage_object.currency,
    #         "coordinates":webpage_object.coordinates,
    #         "description":webpage_object.description}]
    #     session.execute(insert(dbConfig.offer_main_table_name), main_data)
    # except Exception as ex:
    #     InsertMainOfferDataFailed(ex)

    # # Pass data to 'raw data table'
    # try:
    #     raw_data = [{
    #         "raw_data":webpage_object.raw_data}]
    #     session.execute(insert(dbConfig.offer_raw_data_table_name))
    #     session.commit()
    # except Exception

    # try:
    #     # Pass data to details table
    #     table_name=dbConfig.offer_details_table_name
    #     details = webpage_object.details
    #     details = {replace_space_to_floor(key):val for key, val in details.items()}
    #     details = {normalize_column_names(key):val for key, val in details.items()}
    #     detail_names = set(details.keys())
    #     curr_columns = currently_available_column_names(session, table_name)
    #     columns_to_add = detail_names - curr_columns
    #     for column_name in columns_to_add:
    #         add_column(session, table_name, column_name, "text")
    #     details["idL"]=link_db_entry_id
    #     insert_dict_values_to_db(session,
    #                         table_name,
    #                         details)
    # except Exception as ex:
    #     raise InsertDetailsToDBFailed(ex)
        
    # try:
    #     # Pass data to equiplent table
    #     table_name=dbConfig.offer_equipment_table_name
    #     equipment=webpage_object.equipment
    #     if equipment:
    #         equipment=[replace_space_to_floor(eq) for eq in equipment]
    #         equipment=[normalize_column_names(eq) for eq in equipment]
    #         equipment_columns = set(equipment)
    #         equipment_columns_in_db=currently_available_column_names(session, table_name)
    #         columns_to_add = equipment_columns - equipment_columns_in_db
    #         for column_name in columns_to_add:
    #             add_column(session, table_name, column_name, "text")
    #         equipment_dict={eq:True for eq in equipment}
    #         insert_dict_values_to_db(session, table_name, equipment_dict)
    # except Exception as ex:
    #     raise InsertEquipmentToDBFailed(ex)
        




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