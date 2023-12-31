from sqlalchemy import text

def currently_available_column_names(session, table_name) -> set:
    sql = text(f"""SELECT column_name
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{str(table_name)}'""")
    result = session.execute(sql)
    returning_values:set = set()
    for res in result:
        print(res)
        print(type(res))
        returning_values.add(res[0])
    if result:
        return returning_values
    else:
        raise ValueError("No result was returned from db")


def add_column(session, table_name, column_name, column_datatype):
    sql = text(f"""ALTER TABLE {table_name}
    ADD {column_name} {column_datatype}""")
    session.execute(sql)
    session.commit()


def insert_values_to_db(session, table_name, data_dict:dict):
    col_names_list = list(data_dict.keys())
    col_values_list = list(data_dict.values())

    col_names_list = [f"`{name}`" for name in col_names_list]
    columns_parsed = ",".join(col_names_list)
    values_parsed = ",".join([f"\"{val}\"" for val in col_values_list])

    sql = \
    f"""INSERT INTO {table_name} ({columns_parsed}) 
    VALUES ({values_parsed})"""
    print(sql)
    session.execute(text(sql))
    session.commit()