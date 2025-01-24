import cv2
import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *

def bank_statement_image_reshaping(img):
    resize_width = 2400
    resize_height = 2500
    img_resized = cv2.resize(img, (resize_width, resize_height), interpolation=cv2.INTER_LINEAR)
    return img_resized


def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)

    else:
        angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

def extract_year_bank_statement(splited_text):
    sub_text=splited_text
    year_list=year_with_regex(sub_text)
    return year_list

def year_with_regex(date_line):
    date_regex = re.findall(r'\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b', date_line)
    date_regex2 = re.findall(r'\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:-\d{1,2})?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b', date_line)

    if date_regex:
        year_list=date_regex

    elif date_regex2:
        year_list=date_regex2

    else:
        year_list=[]

    return year_list



def bank_statement_data_extract(pdf_path,input_name,target_income_theshold):
    data_list = []
    found_years = []

    # for pdf_path in all_pdfs:
    images = pdf_to_images(pdf_path)
    page_data = {}
    last_year=''
    value_status = False
    name_found = False
    amount_found = False
    year_found = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = bank_statement_image_reshaping(img_bgr)
        img_bgr_resized = deskew(img_bgr_resized)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        data = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
        splited_text=full_text.split('\n')
        splited_text=[x for x in splited_text if x]
        name_found = False
        value_status = False
        year_list=[]
        for idx, i in enumerate(splited_text):
            new_string = i.replace(' ', '')
            if name_found == False:
                name_status = check_name_match(i, input_name)
                if name_status:
                    name_found = True
            elif ('date' in i.lower() or 'for the period' in i.lower() or 'statement period' in i.lower() or 'period' in i.lower() )and not year_list :
                date_line=i
                try:
                    date_line+= ' '+splited_text[idx+1]
                    date_line+= ' '+splited_text[idx+2]
                except:
                    pass

                year_list = extract_year_bank_statement(date_line)

            elif not value_status:
                amount_found=True
                with_sign_ordinary = re.findall(r'(?:ending balance|total value|current balance|ending total value)[A-Za-z/)(\d+\s*,:]*\$\s*([\d+,.]+)', i.lower())
                if with_sign_ordinary:
                    is_valid, value_status = is_less_than_amount(with_sign_ordinary[0], target_income_theshold)

                if not with_sign_ordinary:
                    without_sign = re.findall(r'(?:ending balance|total value|current balance|ending total value)[A-Za-z/)(\d+\s*,:]*\s*([\d+,.]+)', i.lower())
                    if without_sign:
                        is_valid, value_status = is_less_than_amount(without_sign[0],target_income_theshold)
                    else:
                        without_sign = re.findall(r'[A-Za-z\d+\s,:]*\s*([\d+,.]+)', i.lower())
                        if without_sign:
                            is_valid, value_status = is_less_than_amount(without_sign[0], target_income_theshold)

        if name_found  :
            if not year_list:
                year_list=year_with_regex(full_text)
            year_validity_list = []
            for year_value in year_list:
                year_validity_list.append(is_within_3_months(year_value))
            if any(year_validity_list):
                year_validity = True
            else:
                year_validity = False

            if year_list not in found_years:
                found_years.append(year_list)

                data_list.append({'year':year_list,'year_status':year_validity,'name':True,'amount':value_status})


    return data_list


