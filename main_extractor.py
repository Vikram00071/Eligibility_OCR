from identify import *
from FormExtractor import scraper
from FormExtractor import automation_ofac


def main_executor(name,dob,address, user_type, income_type, cdr_number, all_documents,form_types,Business_name,COF,Agreement):
    response = {'id': 'Approved', 'Income_status': 'Not Approved'}
    income_response=False
    ofac_status=True
    cof_status=False
    agree_status=False
    actual_name=name
    if not actual_name:
        actual_name=Business_name
    # ofac_status=automation_ofac.scrap_from_ofac_website(actual_name,address)
    # print(ofac_status)

    if ofac_status:

        try:
            if user_type.lower() == 'individual':
                if income_type.strip().lower() == 'licensed':
                    income_response = scraper.licensed_individual(name,cdr_number)
                else:
                    income_response = main_individual(name,all_documents,income_type,form_types)


            elif user_type.strip().lower() == 'business' or user_type.strip().lower() == 'entity':
                if COF != '':
                    cof_status = cof_extraction(COF, Business_name)
                if Agreement != '':
                    agree_status = agreement_extract(Agreement, Business_name, name)

                if COF and Agreement:
                    if all([cof_status, agree_status]):
                        income_response = True
                if not income_response:
                    if income_type == 'accredited':
                        income_response = main_individual(name, all_documents, income_type, form_types)

                    elif income_type == 'networth':
                        income_response = main_individual(name, all_documents, income_type, form_types)



        except Exception as e:
            pass


    if income_response:
        response = {'id': 'Approved', 'Income_status': 'Approved'}

    return response



