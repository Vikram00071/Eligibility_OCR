import numpy as np
from pytesseract import Output
from FormExtractor.preprocessing_main import *



def extract_year(splited_text):
    year=''
    target_text=splited_text[25:]
    for text in target_text:
        if 'Form 1099-K' in text:
            sub_text=text
            found_years = re.findall(r'\b(20\d{2})\b', sub_text)
            if found_years:
                year = found_years[0]
            break

    return year



def form_1099_K_extract(pdf_path, input_name,threshold):
    found_years = []
    data_list = []

    images = pdf_to_images(pdf_path)

    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        full_text = pytesseract.image_to_string(img_bgr_resized)
        name_found = False

        if '1099-K' in full_text:
            splited_text = full_text.split('\n')
            splited_text = [x for x in splited_text if x]
            d = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
            name_match_status = False
            gross_value_status = False

            n_boxes = len(d['level'])
            for i in range(n_boxes):

                if d['text'][i] == 'FILER’S' and d['left'][i] < 200 and d['top'][i] < 150:

                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 8, y + 50, w + 400, h + 200
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    name = pytesseract.image_to_string(crop_img)
                    name = name.replace('\n', ' ')
                    if name != '':
                        name_found = True
                        name_match_status = check_name_match(name, input_name)
                    else:
                        name_area = ' '.join(splited_text[0:15])
                        name_match_status = check_name_match(name_area, input_name)
                        if name_match_status:
                            name_found = True


                elif d['text'][i] == 'Gross' and d['left'][i] < 1100 and d['top'][i] < 300:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    x, y, w, h = x - 48, y + 60, w + 200, h + 30
                    cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = img_bgr_resized[y:y + h, x:x + w]
                    gross = pytesseract.image_to_string(crop_img)
                    gross = gross.replace('\n', ' ')
                    is_valid, gross_value_status = is_less_than_amount(gross, threshold)


            if name_found and gross_value_status :
                year = extract_year(splited_text)
                if year not in found_years:
                    year_validity = is_year_valid(year)
                    found_years.append(year)
                    data_list.append({'year':year,'year_status':year_validity,'name':name_match_status,'amount':True})

    return data_list





