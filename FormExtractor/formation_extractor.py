import numpy as np
from FormExtractor.preprocessing_main import *


def agreement_extract(pdf_path,input_company_name,input_name):
    status=False
    images = pdf_to_images(pdf_path)
    found_years=[]
    page_data = {}
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        lines = full_text.split('\n')
        splited_text = []
        for line in lines:
            if line.strip():
                splited_text.append(line.strip())
        for idx, i in enumerate(splited_text):
            new_string = i.replace(' ', '')
            input_company_name=clean_string(input_company_name)
            company_name_match_status = check_name_match(full_text, input_company_name)
            name_match_status = check_name_match(full_text, input_name)
            if name_match_status and company_name_match_status:
                status=True
                break

    return status


def certificate_extraction(pdf_path,input_company_name):
    status = False
    certificate=False
    images = pdf_to_images(pdf_path)
    found_years = []
    page_data = {}
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        lines = full_text.split('\n')
        splited_text = []
        for line in lines:
            if line.strip():
                if 'certificate of formation' in lines.lower():
                    certificate=True
                splited_text.append(line.strip())

        for idx, i in enumerate(splited_text):
            new_string = i.replace(' ', '')
            input_company_name = clean_string(input_company_name)
            company_name_match_status = check_name_match(full_text, input_company_name)

            if certificate and company_name_match_status:
                status = True
                break

    return status



