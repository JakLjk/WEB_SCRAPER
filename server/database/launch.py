import sqlalchemy as db
import getpass

from config.server_config import dbConfig


def get_db_engine() -> db.create_engine:

    config = dbConfig

    if config.db_password == None:
        inp = input("Database password was is not specified in config. Do you want to keep passowrd as Null? [y/N]")
        if inp.lower == "n":
            config.db_password = getpass.getpass("Insert your password: ")

    return db.create_engine(f"mariadb+mariadbconnector://{config.db_username}:"\
                            f"{config.db_password}@"\
                            f"{config.db_host}/"\
                            f"{config.db_name}",
                            echo=False,
                            pool_recycle=3600
                            )