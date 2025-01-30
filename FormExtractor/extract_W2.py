import numpy as np
from FormExtractor.preprocessing_main import *

def form_w2_data_extract(pdf_path,input_name,income_threshold):
    found_years = []
    data_list = []


    # for pdf_path in all_pdfs:
    images = pdf_to_images(pdf_path)
    year=''
    value_status = False
    name_found = False
    amount_found = False
    name_match_status = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized, config='--psm 4')
        splited_text=full_text.split('\n')
        splited_text=[x for x in splited_text if x]

        for idx, i in enumerate(splited_text):

            new_string = i.replace(' ', '')
            if ("e/femployee’sname" in new_string.lower()) or ("employee’sname" in new_string.lower()) or ("payer’sname" in new_string.lower()) or ("employer’sname,address,andzipcode" in new_string.lower()) or ("employee'sname,address,andzipcode" in new_string.lower()):
                name_found=True
                name_line = splited_text[idx + 1]
                name_match_status = check_name_match(name_line, input_name)
                if not name_match_status:
                    name_line=splited_text[idx+2]
                    name_match_status = check_name_match(name_line, input_name)

            elif 'wages,tips,othercomp' in new_string.lower() :
                amount_found=True
                ammout = splited_text[idx + 1]
                with_sign_ordinary= re.findall(r'\$([\d,]+(?:\.\d+)?)', ammout)
                if with_sign_ordinary:
                    is_valid, value_status = is_less_than_amount(with_sign_ordinary[0], income_threshold)

                if not with_sign_ordinary:
                    without_sign = re.findall(r'([\d,]+(?:\.\d+)?)', ammout)
                    if without_sign:
                        is_valid, value_status = is_less_than_amount(without_sign[0],income_threshold)
                    else:
                        value = i.strip().split(' ')[0]
                        if 10>len(value)>4:
                            is_valid, value_status = is_less_than_amount(value, income_threshold)

        if name_found and amount_found and name_match_status:
            if year not in found_years and year!='':
                year_validity = is_year_valid(year)
                found_years.append(year)
                data_list.append({'year':year,'year_status':year_validity,'name':name_match_status,'amount':value_status})

    return data_list




