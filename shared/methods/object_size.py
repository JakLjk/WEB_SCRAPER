import sys

def get_object_size(object, unit="MB"):
    units = {
        "MB": 1024**2}
    return round(sys.getsizeof(object) / units[unit],2)
    
