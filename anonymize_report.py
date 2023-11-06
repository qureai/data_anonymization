import hashlib
import re
import pdfplumber
import os
import textract
import html2text
from utils import check_cancer_positive, check_fracture_positive
from docx import Document
import docx2txt
from pydocx import PyDocX

# from comtypes import client


which_os = "None"
try:
    import win32com.client

    which_os = "win"
except:
    pass

# re_dict = {"name": "(NAME|Name|name|Name :|name :)", "dr": "(DR |DR.|Dr |Dr.)"}
re_dict = {
    "name": "(Patient Name :|Patient Name : |Patient Name : |Refd By:)",
    "dr": "(DR |DR.|Dr |Dr.)",
}


def hash_algo(value):
    """Hash the value using sha-224."""
    return str(hashlib.sha224(value.encode("utf-8")).hexdigest())


def doc2txt(input_report_path, final_report_path):
    file_extension = os.path.splitext(input_report_path)[1]

    try:
        if file_extension.lower() == ".docx":
            # Extract text from .docx file using python-docx
            doc = Document(input_report_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            text = "\n".join(paragraphs)
        elif file_extension.lower() == ".doc":
            # Extract text from .doc file using textract
            text = textract.process(input_report_path, encoding="utf-8").decode("utf-8")
        else:
            print("Unsupported file format")
            return

        # Convert and write to final report file
        with open(final_report_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        print(f"Conversion completed. Text saved to {final_report_path}")
    except Exception as e:
        print(f"Error converting {input_report_path}: {e}")


def pdf2txt(input_report_path, final_report_path):
    """generated txt from the pdfs

    Args:
        input_report_path (str): path of the doc/docx file
        final_report_path (str): path to save the generated txt file
    """
    text = ""
    with pdfplumber.open(input_report_path) as pdf:
        for i in range(len(pdf.pages)):
            page = pdf.pages[i]
            text += page.extract_text() + "\n"

    text = text.split("\n")

    check_cancer_positive
    with open(final_report_path.replace(".pdf", ".txt"), "w", encoding="utf-8") as doc:
        for line in text:
            try:
                doc.write(f"{line}\n")
            except:
                continue


def html2txt(input_report_path, final_report_path):
    html = open(input_report_path, "r", encoding="utf-16").read()
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    text_maker.ignore_tables = True
    text_maker.ignore_images = True
    text_maker.ignore_emphasis = False

    text = text_maker.handle(html).replace("\n", "").replace(".", "**").split("**")

    with open(final_report_path.replace(".html", ".txt"), "w", encoding="utf-8") as doc:
        for line in text:
            doc.write(f"{line}\n")


def anonymize_name(entry):
    """Anonymizes the name field in the txt report file
    Args:
        entry ([str]): line from the txt file
    Returns:
        [str]: returns the anonymized name
    """
    anon_name = hash_algo(entry)
    return anon_name


def anonymize_report(txt_report_path, same_line=0):
    """Anonymizes the Patient's and Doctor's name in the '.txt' report file

    Args:
        txt_report_path ([str]): path to the txt file
    """
    with open(txt_report_path, "r", encoding="utf-8", errors="ignore") as file:
        txt_report = file.read()

    # Locate the position of "Patient ID" tag and extract the actual ID
    patient_id_match = re.search(r"Patient ID :\s*\|(\d+)\s*\|", txt_report)
    if patient_id_match:
        patient_id = patient_id_match.group(1)
        txt_report = txt_report.replace(patient_id, anonymize_name(patient_id))

    match = re.search("[Pp]atient [Ii][Dd]", txt_report)

    if match:
        txt_report = txt_report[: match.start()] + "\n" + txt_report[match.start() :]

    txt_list = txt_report.split("\n")
    fracture = check_fracture_positive(txt_list)
    # cancer = check_cancer_positive(txt_list)
    if fracture:
        open(txt_report_path, "w").close()
        txt_list = [str(line) for line in txt_list if line != ""]
        name_done = False

        for i in range(len(txt_list)):
            if name_done == False and re.search(re_dict["name"], txt_list[i]):
                if same_line == i:
                    txt_list[i] = anonymize_name(txt_list[i])
                else:
                    txt_list[i + 1] = anonymize_name(txt_list[i + 1])
                name_done = False

            if re.search(re_dict["dr"], txt_list[i]):
                txt_list[i] = hash_algo(txt_list[i])
            with open(txt_report_path, "a", encoding="utf-8") as f:
                f.write(f"{txt_list[i]}\n")

    else:
        os.remove(txt_report_path)
