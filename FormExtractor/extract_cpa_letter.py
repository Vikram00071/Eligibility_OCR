from boxdetect import config
from boxdetect.pipelines import get_checkboxes
import numpy as np
from FormExtractor.preprocessing_main import *




def extract_expiry_date(date_line):
    date_regex = re.findall(r'(?:\d{4}(?:\s*[./-]|[./-]|[./-]\s*)\d{1,2}(?:\s*[./-]|[./-]|[./-]\s*)\d{1,2}|\d{1,2}(?:\s*[./-]|[./-]|[./-]\s*)\d{1,2}(?:\s*[./-]|[./-]|[./-]\s*)\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b', date_line)
    date_regex2 = re.findall(r'\d{1,4}(?:\s*|,)\b(?:Jan|January|Feb|February|Mar|March|Apr|April|may|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)(?:,|\s*)\d{1,4}\b', date_line)

    if date_regex:
        date_string=date_regex[0]
        parsed_date = parser.parse(date_string)
        current_date = datetime.now()

        return date_string,parsed_date >= current_date
    elif date_regex2:
        date_string = date_regex2[0]
        parsed_date = parser.parse(date_string)
        current_date = datetime.now()

        return date_string, parsed_date >= current_date

    else:
        return '',False



def extract_checkbox(img):
    result=False
    cfg = config.PipelinesConfig()
    cfg.width_range = (30, 55)
    cfg.height_range = (30, 40)
    cfg.scaling_factors = [0.7]
    cfg.wh_ratio_range = (0.5, 1.7)
    cfg.group_size_range = (2, 100)
    cfg.dilation_iterations = 0
    checkboxes = get_checkboxes(
        img, cfg=cfg, px_threshold=0.1, plot=False, verbose=True)
    first_boxes=[]
    second_boxes=[]
    count=0
    if len(checkboxes)>=8:
        if len(checkboxes)==9:
            checkboxes=checkboxes[1:]
        count=1
        for checkbox in checkboxes:
            if count<=4:
                first_boxes.append(checkbox[1])
                count+=1
            else:
                second_boxes.append(checkbox[1])
    if any(first_boxes) and any(second_boxes):
        result=True

    return result



def cpa_extraction(pdf_path,input_name):
    data_list = []

    images = pdf_to_images(pdf_path)

    for page_index, img in enumerate(images):
        name_match_status=False
        date_status=False
        boxesresult=False
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)

        full_text = pytesseract.image_to_string(img_bgr_resized,config='--psm 4')
        splited_text = full_text.split('\n')
        splited_text = [x for x in splited_text if x]

        for idx, i in enumerate(splited_text):
            new_string = i.replace(' ', '')

            if ('investorlegalname:' in new_string.lower()):
                name_found = True
                name_line = i
                name_match_status = check_name_match(name_line, input_name)
                if name_match_status:
                    boxesresult = extract_checkbox(img_bgr_resized)

            if name_match_status and i.lower().startswith('on'):
                actual_date, date_status = extract_expiry_date(i)
                if not date_status:
                    date_line = splited_text[idx - 1] + '' + splited_text[idx - 1]
                    actual_date, date_status = extract_expiry_date(date_line)
                    if not date_status:
                        date_line = splited_text[idx - 1] + ' ' + splited_text[idx] + ' ' + splited_text[idx - 1]
                        actual_date, date_status = extract_expiry_date(date_line.replace(' ', ''))


        if name_match_status and boxesresult and date_status:
            data_list.append({'year': actual_date, 'year_status': True,'name':True,'amount':True})

    return data_list



