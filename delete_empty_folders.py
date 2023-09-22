"""
This file is to search and delete empty folders which are present after 
running the anonymization script to anonymize reports.
There are lots of empty folders once we segregate only positives,
this code takes care of those empty folders.
"""

import os

# Define the directory to start the search from
start_directory = ""  # path of save_directory


def delete_empty_folders(directory):
    for root, dirs, _ in os.walk(directory, topdown=False):
        for folder in dirs:
            folder_path = os.path.join(root, folder)
            if not os.listdir(folder_path):
                try:
                    os.rmdir(folder_path)
                    print(f"Deleted empty folder: {folder_path}")
                except OSError as e:
                    print(f"Error deleting folder {folder_path}: {e}")


delete_empty_folders(start_directory)
