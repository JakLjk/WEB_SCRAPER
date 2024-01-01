import logging

class loggerConfig:
    display_log_level = logging.DEBUG
    max_log_filesize_byte = 5*1024*1024
    log_files_backup_count = 5

class serverConfig:
    bindPort = 4123

    maxThreads = 15
