import os
import glob
from tqdm import tqdm
import shutil
from multiprocessing import Pool
import re


def apply_fun(samples, fun, num_procs=0):
    """applies the provided function to the samples provided and returns the
       output for all samples as list
    Args:
    ----
    samples [list]: list of samples to apply the function
    fun [func]    : a function which is applied to the samples
    num_procs     : number of processors to use in multiprocessing
                    provide value > 0 to invoke multiprocessing
    """
    if num_procs:
        with Pool(num_procs) as p:
            output = p.map(fun, tqdm(samples))
        return output
    else:
        output = []
        for file in tqdm(samples):
            out = fun(file)
            output.append(file)
        return output


def get_files(dir, ext, folder_depth=1):
    """returns sorted list of all the files found of given
    extension in dir
    """
    all_files = []
    for c in range(folder_depth):
        path = os.path.join(dir, "**/" * c + f"*{ext}")
        files = glob.glob(path)
        all_files += files

    return sorted(all_files)


def get_anonymization_path(file, files_dir, save_dir, ext):
    """creates the same folder structure at the save_dir
    and returns the path where the anonymized file will be saved
    """
    target_path = file.replace(files_dir, save_dir)
    if files_dir not in file:
        target_path = os.path.join(save_dir, file.split(os.sep, 1)[1])
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if ext in [".doc", ".docx", ".pdf", ".html"]:
        target_path = target_path.replace(ext, ".txt")
    return target_path


# function to check positive cancer into reports


def check_cancer_positive(report_lines: list):
    rule = "([cC]ancer|[mM]etasta|[mM]align|[cC]arcinoma|[sS]arcoma)"
    negation = "(no |NO |No |not |NOT |Not )"
    present = False
    for line in report_lines:
        if re.search(rule, line) and not re.search(negation, line):
            present = True
            break
    return present


# function to check positive fracture into reports


def check_fracture_positive(report_lines: list):
    rule = "([fF]racture)"
    negation = "(no |NO |No |not |NOT |Not |[Nn]egative |SUGGESTED |rule out)"
    present = False
    for line in report_lines:
        if re.search(rule, line) and not re.search(negation, line):
            present = True
        elif re.search(rule, line) and re.search(negation, line):
            present = False  # Both fracture and negation found in the same line, consider it negative
            break
    return present
