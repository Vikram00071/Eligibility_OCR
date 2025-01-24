import cv2
import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *



def form_1099_R_extract(pdf_path, input_name,threshold):
    found_years = []
    data_list = []

    images = pdf_to_images(pdf_path)

    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        name_found=False

        if '1099-R' in full_text and 'File with Form 1096.' in full_text:
            splited_text=full_text.split('\n')
            d = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
            year=''
            name_match_status=False
            gross_value_status=False
            n_boxes = len(d['level'])
            for i in range(n_boxes):
                if d['text'][i] == 'OMB' and d['left'][i] < 1500 and d['top'][i] < 150 and name_found:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 10, y + 20, w + 200, h + 100
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    year_text = pytesseract.image_to_string(crop_img)
                    years_list = re.findall(r'\b(?:20\d{2}|D0\d{2})\b', year_text)

                    if years_list:
                        year=years_list[0].replace('D','2')
                    else:
                        year_area=False
                        year_text=""
                        splited_text = [x for x in splited_text if x]
                        for text in splited_text:
                            if 'OMB' in text:
                                year_area=True
                            elif '1099-R' in text or 'Transactions' in text:
                                break
                            if year_area==True:
                                year_text+=text+'\n'
                        years_list = re.findall(r'\b(?:20\d{2}|D0\d{2})\b', year_text)
                        if years_list:
                            year=years_list[0].replace('D','2')

                elif d['text'][i].lower() == 'payer’s' and d['left'][i] < 200 and d['top'][i] < 150:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 8, y + 50, w + 550, h + 230
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    name = pytesseract.image_to_string(crop_img)
                    name=name.replace('\n',' ')
                    if name!='':
                        name_found=True
                        name_match_status = check_name_match(name, input_name)
                    else:
                        name_area=' '.join(splited_text[0:15])
                        name_match_status = check_name_match(name_area, input_name)
                        if name_match_status:
                            name_found=True

                elif d['text'][i] == 'Gross' and d['left'][i] < 1250 and d['top'][i] < 250:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 40, y + 40, w + 280, h + 50
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    gross_income_area = pytesseract.image_to_string(crop_img)
                    gross_income_area=gross_income_area.replace('\n',' ')
                    is_valid, gross_value_status = is_less_than_amount(gross_income_area, threshold)

            if name_found and gross_value_status  and year!='':
                if year not in found_years:
                    year_validity = is_year_valid(year)
                    found_years.append(year)
                    data_list.append({'year':year,'year_status':year_validity,'name':name_match_status,'amount':True})

    return data_list




