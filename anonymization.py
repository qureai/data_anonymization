import os
from tqdm import tqdm
from functools import partial
from anonymize_dicoms import anonymize_dicom
from anonymize_report import anonymize_report, doc2txt, pdf2txt, html2txt
import shutil
from utils import get_files, apply_fun, get_anonymization_path


def anonymize_file(file, files_dir, save_dir, ext, same_line=0, other_tags=None):
    try:
        target_path = get_anonymization_path(file, files_dir, save_dir, ext)

        # Exclude temporary files starting with "~$"
        if os.path.basename(file).startswith("~$"):
            return False, file

        if ext in [".doc", ".docx"]:
            doc2txt(file, target_path)
            out = anonymize_report(target_path)
        elif ext == ".pdf":
            pdf2txt(file, target_path)
            out = anonymize_report(target_path, same_line=same_line)
        elif ext == ".html":
            html2txt(file, target_path)
            out = anonymize_report(target_path, same_line=same_line)
        elif ext == ".txt":
            shutil.copy(file, target_path)
            out = anonymize_report(target_path, same_line=same_line)
        else:
            out = anonymize_dicom(file, target_path, other_tags=other_tags)

        return True, True
    except Exception as e:
        print(e)
        print("Not working:", file)
        return False, file


def read_paths_from_file(file_path):
    with open(file_path, "r") as file:
        paths = file.read().splitlines()
    return paths


def save_empty_folder_path(folder_path, ext, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    empty_folder_file_path = os.path.join(save_dir, f"empty_{ext[1:]}_folders.txt")
    with open(empty_folder_file_path, "a") as empty_folder_file:
        empty_folder_file.write(f"{folder_path}\n")


if __name__ == "__main__":
    user_ext = input("Enter the file extension: ").strip().lower()
    depth = 10
    start_idx = 0
    batch_size = 100
    num_procs = 4
    same_line = 0  # for different lines report format
    other_tags = [["0010", "0020"]]

    if user_ext in [".pdf", ".doc", ".docx", ".txt"]:
        ext = user_ext
        files_dir = ""  # input/source path
        save_dir = ""  # destination path

        # Get all files with the specified extension
        all_files = get_files(files_dir, ext, folder_depth=depth)

    elif user_ext == ".dcm":
        ext = ".dcm"
        input_paths_file = ""  # Name of the text file containing paths which is created in "getting_positivecases_folderpath" notebook
        empty_folders_save_dir = (
            ""  # Directory to save empty folder paths where no .dcm is present
        )
        paths = read_paths_from_file(input_paths_file)

        for path in paths:
            new_path = path.replace(
                "save_dir_root_folder_path", "source_dir_root_folder_path"
            )
            files_dir = new_path
            save_dir = path

            # Get all files with the specified extension
            all_files = get_files(files_dir, ext, folder_depth=depth)
            if not all_files:
                save_empty_folder_path(files_dir, ext, empty_folders_save_dir)
                continue

    else:
        print(
            "Unsupported file extension. Please enter .pdf, .doc, .docx, .txt, or .dcm."
        )
        exit()

    if ext:
        end_idx = len(all_files)
        failed_txt_path = os.path.join(files_dir, f"failed_{ext[1:]}.txt")
        print(f"Found {ext} files: {len(all_files)}")

        # Create the save directory if it doesn't exist
        os.makedirs(files_dir, exist_ok=True)

        partial_fun = partial(
            anonymize_file,
            files_dir=files_dir,
            save_dir=files_dir,
            ext=ext,
            same_line=same_line,
            other_tags=other_tags,
        )

        with open(failed_txt_path, "a") as doc:
            for idx in tqdm(range(start_idx, end_idx, batch_size)):
                samples = (
                    all_files[idx : idx + batch_size]
                    if idx + batch_size < end_idx
                    else all_files[idx:end_idx]
                )
                output = apply_fun(samples, partial_fun, num_procs=num_procs)

                for out in output:
                    if not out[0]:
                        doc.write(f"{out[1]}\n")
