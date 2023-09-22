import os
import glob
import shutil
import zipfile
import re
from tqdm import tqdm


def extract_zip_file(source_dir, target_dir):
    zip_files = glob.glob(os.path.join(source_dir, "**/*.zip"), recursive=True)
    
    # Filter zip files based on folder names
    zip_files = [file for file in zip_files if re.search(r"XR", file, re.IGNORECASE)]

    for zip_file in tqdm(zip_files, desc="Extracting"):
        save_path = os.path.join(target_dir, os.path.relpath(os.path.dirname(zip_file), source_dir))
        os.makedirs(save_path, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(save_path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    data_dir = r"E:\KINSOLUTIONS\BACKUP\KCP055"
    save_dir = r"D:\MSK_1209\KCP055"
    extract_zip_file(data_dir, save_dir)
