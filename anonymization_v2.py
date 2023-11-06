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


if __name__ == "__main__":
    # User input
    ext = ".dcm"
    depth = 10
    files_dir = ""
    save_dir = ""
    start_idx = 0
    batch_size = 100
    num_procs = 4
    same_line = 0  # for different lines report format
    other_tags = [["0010", "0020"]]

    # Get all files with the specified extension
    all_files = get_files(files_dir, ext, folder_depth=depth)

    end_idx = len(all_files)
    failed_txt_path = os.path.join(save_dir, f"failed_{ext[1:]}.txt")
    print(f"Found {ext} files: {len(all_files)}")

    # Create the save directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    partial_fun = partial(
        anonymize_file,
        files_dir=files_dir,
        save_dir=save_dir,
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
