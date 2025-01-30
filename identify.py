#Importing Modules
from FormExtractor.extract_1099_B import *
from FormExtractor.extract_1099_INT import *
from FormExtractor.extract_1099_K import *
from FormExtractor.extract_1099_DIV import *
from FormExtractor.extract_1099_MISC import *
from FormExtractor.extract_1099_NEC import *
from FormExtractor.extract_1099_S import *
from FormExtractor.extract_1099_SA import *
from FormExtractor.extract_1099_R import *
from FormExtractor.extract_1040 import *
from FormExtractor.extract_1065 import *
from FormExtractor.extract_1065_entity import *
from FormExtractor.extract_W2 import *
from FormExtractor.extract_client_statement import *
from FormExtractor.extract_cpa_letter import *
from FormExtractor.extract_bank_statement import *
from FormExtractor.formation_extractor import *
from FormExtractor.preprocessing_main import *



def extract_pdf_text_for_1099_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type=''
    detection=False
    regex_1099list = ['1099-B', '1099-INT', '1099-DIV', '1099-K', '1099-MISC', '1099-NEC', '1099-R', '1099-SA', '1099-S']
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)
        for reg in regex_1099list:
            if reg in text:
                form_type=reg
                detection=True

        if detection:
            break


    return form_type



def extract_pdf_text_for_1065_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type=''
    detection=False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)
        if re.findall(r'Schedule K-1',text) :
            form_type = '1065k'
            detection=True
        elif (re.findall(r'Form 1065|Form1065|1065 Form', text)) or ('Form 1065' in text):
            form_type = '1065'
            detection = True

        if detection:
            break

    return form_type




def extract_pdf_text_for_1040_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type = ''
    detection = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)

        if (re.findall(r'Form1040|Form 1040|1040 Form', text)) and (not re.findall(r'Form 1065|Form1065|1065 Form', text)):
            form_type = '1040'
            detection = True


        if detection:
            break

    return form_type


def extract_pdf_text_for_bank_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type = ''
    detection = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)

        if re.findall(r'Bank Statement|BANK STATEMENT', text):
            form_type = 'bank'
            detection = True
        if detection:
            break

    return form_type



def extract_pdf_text_for_cpa_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type = ''
    detection = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)

        if 'accreditedinvestorverificationletter' in text.lower().replace(' ','') or 'investorlegalname' in text.lower().replace(' ',''):
            form_type = 'CPA'
            detection = True

        if detection:
            break

    return form_type




def extract_pdf_text_for_w2_detection(pdf_path):
    images = pdf_to_images(pdf_path)
    form_type = ''
    detection = False
    for page_index, img in enumerate(images):
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_bgr_resized = image_reshaping(img_bgr)
        text = pytesseract.image_to_string(img_bgr_resized)

        if (re.findall(r'W-2|Form W-2', text)):
            form_type = 'W2'
            detection = True


        if detection:
            break

    return form_type


def for_1099(name,pdf_files,threshold):
    list_1099=[]
    for file in pdf_files:
        form_type=extract_pdf_text_for_1099_detection(file)
        if form_type!='':
            print('detected',form_type)
            if form_type=='1099-B':
                datalist = form_1099_B_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)

            elif form_type=='1099-INT':

                datalist = form_1099_INT_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)


            elif form_type=='1099-DIV':
                datalist = form_1099_div_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)

            elif form_type=='1099-K':
                datalist = form_1099_K_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)


            elif form_type=='1099-MISC' :
                datalist = form_1099_MISC_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)


            elif form_type=='1099-NEC':
                datalist = form_1099_NEC_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)

            elif form_type=='1099-R' :
                datalist = form_1099_R_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)


            elif form_type=='1099-S' :
                datalist = form_1099_S_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)

            elif form_type=='1099-SA':
                datalist = form_1099_SA_extract(file, name,threshold)
                for data in datalist:
                    list_1099.append(data)

        else:
            pass

    return list_1099









def for_1065(name,pdf_files,income_threshold):
    years_1065k=[]
    list_1065 = []
    list_1065k=[]
    final_1065k_list=[]
    for file in pdf_files:
        form_type = extract_pdf_text_for_1065_detection(file)
        print('detected',form_type)
        if form_type=='1065':
            data_1065list = form_1065_extractor(file, name, income_threshold)
            for data in data_1065list:
                list_1065.append(data)

        elif form_type=='1065k':
            data_1065klist = form_1065k_data_extract(file, name, income_threshold,years_1065k)
            for data in data_1065klist:
                list_1065k.append(data)

    if len(list_1065k)>0:
        for data in list_1065k:
            ordinary_income_amount, ordinary_income_status = is_less_than_amount(str(data['amount']), income_threshold)
            if data['name'] and data['year_status'] and ordinary_income_status:
                final_1065k_list.append({'year': data['year'], 'year_status': True, 'name': True, 'amount': True})

    if final_1065k_list:
        return final_1065k_list
    else:
        return list_1065





def for_Client(name,pdf_files,income):
    client_status = False
    list_client = []
    for file in pdf_files:
        form_type = extract_pdf_text_for_cpa_detection(file)

        if form_type == 'client':
            client_datalist = client_statement_data_extract(file, name, income)
            for data in client_datalist:
                list_client.append(data)



    if len(list_client) > 0:
        for entry in list_client:
            if entry['year_status'] and entry['name'] and entry['amount']:
                client_status = True

    return client_status


def for_CPA(name,pdf_files,income):
    cpa_status=False
    list_cpa = []
    for file in pdf_files:
        form_type = extract_pdf_text_for_cpa_detection(file)
        if form_type == 'CPA':
            data_cpa_list = cpa_extraction(file,name)
            for data in data_cpa_list:
                list_cpa.append(data)


    if len(list_cpa) > 0:
        for entry in list_cpa:
            if entry['year_status'] and entry['name'] and entry['amount']:
                cpa_status=True


    return cpa_status



def for_Bank(name,pdf_files,income):
    bank_status=False
    list_bank = []
    for file in pdf_files:
        form_type = extract_pdf_text_for_bank_detection(file)

        if form_type == 'bank':
            bank_datalist = bank_statement_data_extract(file, name, income)
            for data in bank_datalist:
                list_bank.append(data)

    if len(list_bank) > 0:
        for entry in list_bank:
            if entry['year_status'] and entry['name'] and entry['amount']:
                bank_status=True


    return bank_status




def for_1040(name,pdf_files,threshold):
    list_1040 = []
    for file in pdf_files:
        form_type = extract_pdf_text_for_1040_detection(file)

        if form_type:
            print('detected',form_type)
            data_1040list = form_1040_data_extract(file, name,threshold)

            for data in data_1040list:
                list_1040.append(data)


    return list_1040



def for_W2(name,pdf_files,income_threshold):
    list_w2 = []
    for file in pdf_files:
        form_type = extract_pdf_text_for_w2_detection(pdf_files)
        if form_type:
            print('detected',form_type)
            data_w2list = form_w2_data_extract(file, name, income_threshold)
            for data in data_w2list:
                list_w2.append(data)

    return list_w2



def check_forms_eligibilty(output):
    income_status=False
    previous_years = []
    Final_status = False
    count = 1
    if len(output) > 0:
        for entry in output:
            if entry['year'] not in previous_years and entry['year_status'] and entry['name'] and entry['amount']:
                previous_years.append(entry['year'])

                if count == 2:
                    income_status = True
                count += 1



    return income_status



def make_list(lists):

    final_list = []
    for item in lists:
        if len(item) > 0:
            final_list.append(item[0])

    return final_list

def cof_extraction(pdf_file,business_name):
    cof_status=certificate_extraction(pdf_file,business_name)
    return cof_status

def agrement_extraction(pdf_file,business,name):
    a_status = agreement_extract(pdf_file, business,name)
    return a_status






def main_individual(name,pdf_files,income,form_type):
    output = []
    income_status=False
    income_threshold=200000
    if income.lower().startswith('joint'):
        income_threshold=300000


    status = False

    if "CPA" in form_type :
        status = for_CPA(name, pdf_files,income)

    if ('Bank' in form_type or 'Bank Statement' in form_type) and status == False:
        status = for_Bank(name, pdf_files,income)

    if ('Client' in form_type or 'Client Statement' in form_type) and status == False:
        status = for_Client(name, pdf_files,income)


    if not status:

        for i in form_type:
            if i.strip().startswith('1099'):
                data_list1099 = for_1099(name, pdf_files,income_threshold)
                for data in data_list1099:
                    output.append(data)


            elif i.strip().startswith('1040'):
                data_list1040 = for_1040(name, pdf_files,income_threshold)
                for data in data_list1040:
                    output.append(data)

            elif i.strip().startswith('1065'):
                data_list1065 = for_1065(name, pdf_files,income_threshold)
                for data in data_list1065:
                    output.append(data)

            elif i.strip().startswith("W2"):
                data_list2 = for_W2(name, pdf_files,income_threshold)
                for data in data_list2:
                    output.append(data)

        income_status=check_forms_eligibilty(output)

    else:
        income_status=True




    return income_status

