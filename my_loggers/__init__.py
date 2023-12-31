from .setup_logger import setup_logger


setup_logger("MAIN_LOG", "main_logging.log")
setup_logger("SERV_LOG", "server_log.log")
setup_logger("CLIENT_LOG", "client_log.log")
setup_logger("DB_LOG", "db_log.log")

# setup_logger("MAIN_LOG")
# setup_logger("SERV_LOG")
# setup_logger("CLIENT_LOG")
# setup_logger("DB_LOG")