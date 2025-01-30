import numpy as np
import pytesseract
from pytesseract import Output
import cv2
import re
from FormExtractor.preprocessing_main import *
def form_1065_extractor(pdf_path,input_name,income_threshold):
    found_years=[]
    data_list=[]
    # for pdf_path in all_pdfs:
    images = pdf_to_images(pdf_path)
    ordinary_status = False
    net_earning_status = False
    total_asset_status = False
    net_income_status = False
    end_year_status = False
    name_match_status = False

    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        img_bgr_resized = image_reshaping(img_bgr)
        data = pytesseract.image_to_data(img_bgr_resized, output_type=Output.DICT)
        full_text = pytesseract.image_to_string(img_bgr_resized,config='--psm 4')
        splited_text = full_text.split('\n')
        splited_text = [x for x in splited_text if x]


        for idx,i in enumerate(splited_text):
            new_string=i.replace(' ','')

            if ('aprincipalbusiness' in new_string.lower()) or ("nameofpartnership" in new_string.lower()):
                name_line = splited_text[idx + 1]
                name_match_status = check_name_match(name_line, input_name)
                if not name_match_status :
                    name_line = splited_text[idx + 2]
                    name_match_status = check_name_match(name_line, input_name)

            elif '23ordinarybusinessincome(loss)' in new_string.lower():
                ordinary = re.findall(r'\$([\d+,.]+)', i)
                if ordinary:
                    cleaned_ordinary_income, ordinary_status = is_less_than_amount(ordinary[0], income_threshold)
                if not ordinary:
                    ordinary = re.findall(r'subtract line+[.\d+A-Za-z-\s*]+(?:23)?\s+([\d,]+(?:\.\d+)?)', i.lower())
                    if ordinary:
                        cleaned_ordinary_income, net_earning_status = is_less_than_amount(ordinary[0], income_threshold)


            elif ('netearnings(loss)fromself-employment' in new_string.lower()) or ('net earnings (loss) from self-employment' in new_string.lower()):
                net_earning = re.findall(r'\$([\d+,.]+)', i)
                if net_earning:
                    cleanednet_earning_income, net_earning_status = is_less_than_amount(net_earning[0], income_threshold)
                if not net_earning:
                    net_earning = re.findall(r'self-employment+[.\d+A-Za-z-\s*]+(?:14)?\s+([\d,]+(?:\.\d+)?)', i.lower())
                    if net_earning:
                        cleanednet_earning_income, net_earning_status = is_less_than_amount(net_earning[0], income_threshold)


            elif 'totalassets' in new_string.lower()[0:15]:
                total_asset=re.findall(r'\$([\d+,.]+)',i)
                if total_asset:
                    cleaned_assest_income, total_asset_status = is_less_than_amount(total_asset[0], 5000000.0)
                if not total_asset:
                    total_asset = re.findall(r'total assets|totalassets+[.\d+A-Za-z-\s*]+\s+([\d,]+(?:\.\d+)?)', i.lower())
                    if total_asset:
                        cleaned_assest_income, total_asset_status = is_less_than_amount(total_asset[0], 5000000.0)


            elif 'netincome(loss)(seeinstructions)' in new_string.lower():
                net_income = re.findall(r'\$([\d+,.]+)', i)
                if net_income:
                    cleaned_net_income, net_income_status = is_less_than_amount(net_income[0], income_threshold)
                if not net_income:
                    net_income = re.findall(r'net income+[.\d+A-Za-z-()\s*]+\s+([\d,]+(?:\.\d+)?)', i.lower())
                    if net_income:
                        cleaned_net_income, net_income_status = is_less_than_amount(net_income[0], income_threshold)

            elif 'balanceatendofyear' in new_string.lower():
                vv=i.lower()
                end_year_balance = re.findall(r'\$([\d+,.]+)', i)
                if end_year_balance:
                    end_year_income, end_year_status = is_less_than_amount(end_year_balance[0], 5000000.0)
                if not end_year_balance:
                    end_year_balance = re.findall(r'end\s*of\s*year[.\dA-Za-z-()\s*]+\s+([\d,]+(?:\.\d+)?)', i.strip().lower())
                    if end_year_balance:
                        end_year_income, end_year_status = is_less_than_amount(end_year_balance[0], 5000000.0)

            if ordinary_status or net_earning_status  or total_asset_status or (net_income_status and end_year_status) :
                year = extract_year(splited_text, data, img_bgr_resized)
                if year not in found_years:
                    year_validity = is_year_valid(year)
                    found_years.append(year)
                    data_list.append({'year': year, 'year_status': year_validity, 'name': name_match_status, 'amount': True})


    return data_list


