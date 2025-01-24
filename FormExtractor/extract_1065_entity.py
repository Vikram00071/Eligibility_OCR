import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *


def extract_year(splited_text,data,img_bgr_resized):
    year=''
    sub_text=splited_text[-1]
    found_years = re.findall(r'\b(20\d{2})\b', sub_text)
    if found_years and len(found_years[0])==4:
        year = found_years[0]
    else:
        sub_text = splited_text[-2]
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


def form_1065k_data_extract(pdf_path,input_name,income_threshold,found_years):
    data_list=[]
    # for pdf_path in all_pdfs:
    images = pdf_to_images(pdf_path)
    name_found = False
    name_match_status=False
    for page_index, img in enumerate(images):
        if name_found==False:
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
            img_bgr_resized = image_reshaping(img_bgr)
            data = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
            full_text = pytesseract.image_to_string(img_bgr_resized)
            splited_text=full_text.split('\n')
            splited_text = [x for x in splited_text if x]

            for idx,i in enumerate(splited_text):
                new_string=i.replace(' ','')
                if ('instructions'in new_string.lower() or 'shareholder' in new_string.lower()) and 'name,address,city,state' in new_string.lower():
                    name_line = splited_text[idx + 1]
                    name_match_status = check_name_match(name_line, input_name)
                    name_found=True
                    break

            if name_found:
                for i in range(len(data['text'])):
                    if data['text'][i]=="Ordinary" and data['text'][i+1]=="business" :
                        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        y, x, h, w = y + 30, x + 70, h + 30, w + 200
                        cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        crop_img3 = img_bgr_resized[y:y + h, x:x + w]
                        ordinary_income_area = pytesseract.image_to_string(crop_img3)
                        ordinary_income_area = ordinary_income_area.replace('\n', '')
                        ordinary_income_amount, ordinary_income_status = is_less_than_amount(ordinary_income_area, income_threshold)
                        year = extract_year(splited_text, data, img_bgr_resized)
                        year_validity = is_year_valid(year)
                        if (year not in found_years) and (year_validity):
                            found_years.append(year)
                            data_list.append({'year': year, 'year_status': year_validity, 'name': name_match_status, 'amount': ordinary_income_amount})
                        elif (year in found_years) and (year_validity):
                            for data in data_list:
                                if data['year']==year:
                                    data['amount']+=ordinary_income_amount

                        break

    return data_list


#

