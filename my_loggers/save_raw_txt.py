import pathlib
import os

def save_raw(filename:str, raw_data:str):
    path_to_ss_folder = pathlib.Path(__file__).parent.resolve()
    path_to_file = f"{path_to_ss_folder}/saved_raw_for_verification/{filename}.txt"
    with open(path_to_file, "w", encoding="utf-8") as f:
        f.write(raw_data)

