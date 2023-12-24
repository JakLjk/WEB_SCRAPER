import logging

main_log = logging.getLogger("MAIN_LOG")

class Communication():
    def __repr__(self) -> str:
        pass

    def __init__(self) -> None:
        self._machine_id:str=None
        self._command:str=None
        self._data:str=None
        self._data_obj_name:str=None
    
    def set_comm_details(self,
                         command:str,
                         data_to_pass=None):
        self._command=None
        self._data=None
        self._data_obj_name=None

        self._command = command

        if data_to_pass:
            # self._data_obj_name = data_to_pass.__name__
            self._data = data_to_pass

    def get_command(self):
        return self._command

    def get_data(self):
        return self._data

