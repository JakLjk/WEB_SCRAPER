import pathlib
import logging

from config.main_config import loggerConfig

def setup_logger(name:str, filename:str=None):
    new_log = logging.getLogger(name)
    new_log.setLevel(logging.DEBUG)

    m_formatter = logging.Formatter('|%(name)s| %(asctime)s - %(levelname)s - %(message)s')
    
    if filename:
        path_to_log_folder = pathlib.Path(__file__).parent.resolve()

        fh = logging.FileHandler(f"{path_to_log_folder}/{filename}")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(m_formatter)
        new_log.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(loggerConfig.display_log_level)
    sh.setFormatter(m_formatter)
    new_log.addHandler(sh)

    new_log.debug(f"{name} initialised")