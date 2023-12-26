import logging


class Communication():
    def __repr__(self) -> str:
        pass

    def __init__(self) -> None:
        self._machine_id:str=None
        self._command:str=None
        self._data:str=None
        self._data_obj_name:str=None
        self.additional_variables:dict=None
    
    def set_comm_details(self,
                         command:str,
                         status:str=None,
                         data_to_pass=None,
                         additional_variables:dict=None):
        self._command=None
        self._status=None
        self._data=None
        self._data_obj_name=None

        self._command = command

        if data_to_pass:
            self._data = data_to_pass
        if additional_variables:
            self.additional_variables = additional_variables

    def get_command(self):
        return self._command
    
    def get_status(self):
        return self._status
    
    def get_additional_variables(self):
        return self.additional_variables

    def get_data(self):
        return self._data

