from doctr.models import ocr_predictor
from doctr.io import DocumentFile
from FormExtractor.preprocessing_main import *
import os
from passporteye import read_mrz
ocr = ocr_predictor(pretrained=True,assume_straight_pages=False,straighten_pages=True)


def get_id_text(image_path,ext):
    if ext=='pdf':
        doc = DocumentFile.from_pdf(image_path)
    else:
        doc = DocumentFile.from_images(image_path)
    result = ocr(doc)
    text = result.render()
    full_text = text.replace('\n', ' ')

    return full_text



def id_mapping(image_path,name,dob,ext):
    full_text = get_id_text(image_path,ext)
    name_status = check_name_match(full_text, name)
    date_status = match_id_dob(full_text, dob)
    if name_status and (not date_status):
        if ext=='pdf':
            images=pdf_to_images2(image_path)
            pilimage=images[0]
            pilimage.save('temp.jpg')
            mrz = read_mrz('temp.jpg')
            os.remove('temp.jpg')

        else:
            mrz = read_mrz(image_path)

        if mrz:
            mrz=mrz.to_dict()
            extracted_date=mrz['date_of_birth']
            date_status=passport_date_extraction(extracted_date,dob)

    if name_status and date_status:
        result='Id Approved'
    else:
        result='Id Not Approved'

    return result






