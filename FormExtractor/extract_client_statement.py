import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *

def extract_year_client_statement(splited_text):
    year=''
    sub_text=splited_text
    found_years = re.findall(r'\b(20\d{2})\b', sub_text)
    if found_years and len(found_years[0])==4:
        year = found_years[0]
    return year

def year_with_regex(date_line):
    date_regex = re.findall(r'\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b', date_line)
    date_regex2 = re.findall(r'\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:-\d{1,2})?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b', date_line)

    if date_regex:
        found_years = re.findall(r'\b(20\d{2})\b', date_regex2[0])
        if found_years:
            actual_year = found_years[0]
    elif date_regex2:
        found_years = re.findall(r'\b(20\d{2})\b', date_regex2[0])
        if found_years:
            actual_year=found_years[0]

    else:
        actual_year=''

    return actual_year


data_list=[]
def client_statement_data_extract(pdf_path,input_name,target_income_theshold):
    found_years = []
    # if income_type.lower() == 'joint':
    #     target_income_theshold = 300000.0
    # else:
    #     target_income_theshold = 200000.0

    images = pdf_to_images(pdf_path)
    page_data = {}
    last_year=''
    value_status = False

    amount_found = False
    year_found=False
    date_found=False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        data = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
        splited_text=full_text.split('\n')
        splited_text=[x for x in splited_text if x]
        name_found = False
        value_status= False

        for idx, i in enumerate(splited_text):
            new_string = i.replace(' ', '')
            if name_found==False:
                name_status=check_name_match(i,input_name)
                if name_status:
                    name_found=True
            if 'date' in i.lower() or 'for the period' in i.lower() or 'statement period' in i.lower() or 'period' in i.lower():
                date_line = i
                try:
                    date_line += ' ' + splited_text[idx + 1]
                    date_line += ' ' + splited_text[idx + 2]
                except:
                    pass
                year = extract_year_client_statement(date_line)
                if year != '':
                    year_value = year
                    year_found = True
            if not value_status:
                amount_found=True
                with_sign_ordinary = re.findall(r'(?:ending total value|total ending value|total value|current balance|current value|account value|market value|account market value|ending value)\s* ([(/)A-Za-z\d\s,]+) (\$\d+,+\d+.\d+)', i.lower())

                if with_sign_ordinary:
                    is_valid, value_status = is_less_than_amount(with_sign_ordinary[0][0], target_income_theshold)

                if not with_sign_ordinary:
                    without_sign = re.findall(r'(?:ending total value|total ending value|total value|current balance|current value|account value|market value|account market value|ending value)\s* (?:\d+,+\d+.\d+|\$\d+,+\d+.\d+)', i.lower())
                    if without_sign:
                        is_valid, value_status = is_less_than_amount(without_sign[0],target_income_theshold)
                    else:
                        without_sign = re.findall(r'[A-Za-z\d+\s,:]*\s*([\d+,.]+)', i.lower())
                        if without_sign:
                            is_valid, value_status = is_less_than_amount(without_sign[0], target_income_theshold)

        if name_found  and value_status:
            if year=='':
                year_value=year_with_regex(full_text)
            if year_value not in found_years:
                year_validity = is_year_valid(year_value)
                found_years.append(year_value)

                data_list.append({'year':year_value,'year_status':year_validity,'name':True,'amount':True})

    return data_list




