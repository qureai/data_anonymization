
import multiprocessing
from contextlib import closing
import pandas as pd
from tqdm import tqdm
import pydicom
import hashlib
import glob
import os
import re


DCM_HEADER = str.encode(
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    "\x00\x00\x00\x00\x00\x00\x00\x00\x00DICM"
)

re_dict = {"name": "(NAME|Name|name)", "dr": "(DR |DR.|Dr |Dr.)"}


def hash_algo(value):
    """Hash the value using sha-224."""
    return str(hashlib.sha224(value.encode("utf-8")).hexdigest())


def is_valid_dicom(file_path):
    file_obj = open(file_path, "rb").read()
    return DCM_HEADER in file_obj


def get_filepath_list(path, ext):
    """return all filepaths in path end with ext"""
    return glob.glob(os.path.join(path, "**/**/*" + ext), recursive=True)


def anonymize_dicom(input_dicom_path, final_dicom_path, other_tags=[]):
    plan = pydicom.read_file(input_dicom_path, force=True)
    for d in plan:
        if d.VR == "PN" or "institution" in d.name.lower():
            if type(d.value)==pydicom.multival.MultiValue:
                d.value = hash_algo(''.join([str(i) for i in list(d.value)]))
            else:
                d.value = hash_algo(d.value)
        if other_tags:
            for tag in other_tags:
                plan[tag].value = hash_algo(plan[tag].value)
    pydicom.write_file(final_dicom_path, plan)
