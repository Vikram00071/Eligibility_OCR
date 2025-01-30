import numpy as np
import pytesseract
from pytesseract import Output
import cv2
import re
from FormExtractor.preprocessing_main import *



def extract_year(splited_text,data,img_bgr_resized):
    year=''
    sub_text=splited_text[-1]
    found_years = re.findall(r'\b(20\d{2})\b', sub_text)
    if found_years:
        year = found_years[0]
    else:
        sub_text = splited_text[-1]
        found_years = re.findall(r'\b(20\d{2})\b', sub_text)
        if found_years:
            year = found_years[0]


    if year=='':
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            if data['text'][i] == 'OMB' and data['left'][i] < 1250 and data['top'][i] < 250:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                x = x - 200
                y = y - 50
                h = h + 60
                w = w + 150
                crop_img = img_bgr_resized[y:y + h, x:x + w]
                year_text = pytesseract.image_to_string(crop_img)
                found_years = re.findall(r'\b(20\d{2})\b', year_text)
                if found_years:
                    year=found_years[0]

    return year


def check_name_coordinates(data,img_bgr_resized):
    last_name=False
    first_name=False
    first_name_area=''
    last_name_area=''
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        if data['text'][i] == 'first' and data['left'][i] < 200 and data['top'][i] < 500 and not first_name:
            first_name=True
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            x = x - 80
            y = y + 14
            h = h + 40
            w = w + 380
            crop_img = img_bgr_resized[y:y + h, x:x + w]
            first_name_area = pytesseract.image_to_string(crop_img)
            first_name_area = first_name_area.replace('\n', '')


        elif data['text'][i] == 'Last' and data['left'][i] < 800 and data['top'][i] < 500 and not last_name:
            last_name=True
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            x = x - 17
            y = y + 12
            h = h + 40
            w = w + 260
            cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
            last_name = True
            crop_img1 = img_bgr_resized[y:y + h, x:x + w]
            last_name_area = pytesseract.image_to_string(crop_img1)
            last_name_area = last_name_area.replace('\n', '')

    full_name=first_name_area+' '+last_name_area
    return full_name





def form_1040_data_extract(pdf_path,input_name,threshold):
    found_years = []
    data_list = []
    # for pdf_path in all_pdfs:
    images = pdf_to_images(pdf_path)
    page_data = {}
    last_year=''
    value_status = False
    name_found = False
    amount_found = False
    for page_index, img in enumerate(images):

        name_match_status = False
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        data = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
        splited_text=full_text.split('\n')
        splited_text=[x for x in splited_text if x]

        for idx, i in enumerate(splited_text):

            new_string = i.replace(' ', '')
            if ('yourfirstname' in new_string.lower()) :
                name_found=True
                name_line = splited_text[idx + 1]
                name_match_status = check_name_match(name_line, input_name)
                if not name_match_status:
                    name_line=splited_text[idx+2]
                    name_match_status = check_name_match(name_line, input_name)



            elif 'adjustedgrossincome' in new_string.lower():
                amount_found=True
                with_sign_ordinary= re.findall(r'\$(?:\s*)?([\d,]+(?:\.\d+)?)+)', i)
                if with_sign_ordinary:
                    cleaned_income = clean_currency_string(with_sign_ordinary[0])
                    is_valid, value_status = is_less_than_amount(with_sign_ordinary[0], threshold)

                if not with_sign_ordinary:
                    without_sign = re.findall(r'gross income+[.\d+A-Za-z-\s*]+(?:11)?\s+([\d,]+(?:\.\d+)?)', i.lower())
                    if without_sign:
                        cleaned_income = clean_currency_string(without_sign[0])
                        is_valid, value_status = is_less_than_amount(without_sign[0],threshold)
                    else:
                        value = i.strip().split(' ')[-1]
                        if 10>len(value)>4:
                            cleaned_income = clean_currency_string(value)
                            is_valid, value_status = is_less_than_amount(value, threshold)



        if name_found and amount_found:
            year = extract_year(splited_text, data, img_bgr_resized)
            if year not in found_years and year!='':
                year_validity = is_year_valid(year)
                found_years.append(year)
                data_list.append({'year':year,'year_status':year_validity,'name':name_match_status,'amount':value_status})


    return data_list



