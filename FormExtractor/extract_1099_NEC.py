import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *


def extract_year(splited_text):
    year=''
    target_text=splited_text[25:]
    for text in target_text:
        if 'Form 1099-NEC' in text:
            sub_text=text
            found_years = re.findall(r'\b(20\d{2})\b', sub_text)
            if found_years:
                year = found_years[0]
            break

    return year


def form_1099_NEC_extract(pdf_path, input_name,threshold):
    found_years = []
    data_list = []

    images = pdf_to_images(pdf_path)
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        name_found = False
        non_employee_value_status=False
        if '1099-NEC' in full_text:
            splited_text = full_text.split('\n')
            splited_text = [x for x in splited_text if x]
            d = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
            name_match_status = False
            interest_value_status = False

            n_boxes = len(d['level'])
            for i in range(n_boxes):

                if d['text'][i] == 'PAYER’S' and d['left'][i] < 250 and d['top'][i] < 180:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 10, y + 50, w + 680, h + 210
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    name = pytesseract.image_to_string(crop_img)
                    name=name.replace('\n',' ')
                    if name != '':
                        name_found = True
                        name_match_status = check_name_match(name, input_name)
                    else:
                        name_area = ' '.join(splited_text[0:15])
                        name_match_status = check_name_match(name_area, input_name)
                        if name_match_status:
                            name_found = True



                elif d['text'][i] == 'Nonemployee' and d['left'][i] < 1200 and d['top'][i] < 500:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 48, y + 25, w + 200, h + 30
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    non_employee_area = pytesseract.image_to_string(crop_img)
                    non_employee_area = non_employee_area.replace('\n', '')
                    is_valid, non_employee_value_status = is_less_than_amount(non_employee_area, threshold)


            if name_found and non_employee_value_status :
                year = extract_year(splited_text)
                if year not in found_years:
                    year_validity = is_year_valid(year)
                    found_years.append(year)
                    data_list.append({'year':year,'year_status':year_validity,'name':name_match_status,'amount':True})

    return data_list




