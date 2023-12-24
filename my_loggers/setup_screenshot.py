import pathlib
import os


def save_screenshot_to_folder_as(filename:str, extension="png"):
    path_to_ss_folder = pathlib.Path(__file__).parent.resolve()
    path_to_file = f"{path_to_ss_folder}/screenshots/{filename}.{extension}"
    i = 0
    while True:
        i += 1 
        if os.path.isfile(path_to_file):
            new_filename = f"{filename}_{i}"
            path_to_file = f"{path_to_ss_folder}/screenshots/{new_filename}.{extension}"
        else:
            return path_to_file

            
