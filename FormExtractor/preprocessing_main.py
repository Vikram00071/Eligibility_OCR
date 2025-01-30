from pdf2image import convert_from_path
from datetime import datetime, timedelta
import cv2
import re
import pytesseract
from dateutil import parser
# from datetime import datetime, timedelta


def pdf_to_images(pdf_path):
    """Convert each page of the PDF to an Image."""
    return convert_from_path(pdf_path, dpi=800)
    # return convert_from_path(pdf_path, dpi=800,poppler_path=r'C:\Users\Vikram\Desktop\khera_project - Copy\poppler-21.11.0\Library\bin')

def pdf_to_images2(pdf_path):
    """Convert each page of the PDF to an Image."""
    return convert_from_path(pdf_path,dpi=100)


def image_reshaping(img):
    """Resize the image to a specific width and height."""
    resize_width = 2000
    resize_height = 2500
    img_resized = cv2.resize(img, (resize_width, resize_height), interpolation=cv2.INTER_LINEAR)
    return img_resized


def is_year_valid(year):
    year_validity=False
    current_year = datetime.now().year
    valid_years = [str(current_year - 1), str(current_year - 2),str(current_year - 3),str(current_year)]
    if year in valid_years:
        year_validity=True

    return year_validity

def clean_string(value):
    special_values=['on ','as of ','(',')',',']
    for item in special_values:
        value = value.replace(item, '')
    return value

def clean_currency_string(currency_string: str) -> float:
    currency_string=currency_string.strip()
    cleaned_string = re.sub(r'[^\d.]', '', currency_string)

    try:
        value = float(cleaned_string)
        return value
    except ValueError as e:
        # print(f"Error converting '{currency_string}' to float: {e}")
        return 0.0

def is_less_than_amount(currency_string: str, amount: float = 200000.0) -> bool:
    value = clean_currency_string(currency_string)
    return value, value >= amount


def check_name_match(name_area, input_name):
    input_name_words = input_name.split()
    name_area_lower = name_area.lower()
    if all(word.lower() in name_area_lower for word in input_name_words):
        name_match = True

    else:
        name_match = False

    return name_match

def check_name_match_again(name_area, input_name):
    input_name_words = input_name.split()
    name_area_lower = name_area.lower()
    name_area_lower=name_area_lower.replace(' ','').lower()
    if all(word.lower() in name_area_lower for word in input_name_words):
        name_match = True
    else:
        name_match = False

    return name_match

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
            if data['text'][i] == 'OMB' and data['left'][i] < 1350 and data['top'][i] < 250:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                x = x - 200
                y = y - 50
                h = h + 60
                w = w + 150
                # cv2.rectangle(img_bgr_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                crop_img = img_bgr_resized[y:y + h, x:x + w]
                year_text = pytesseract.image_to_string(crop_img)
                found_years = re.findall(r'\b(20\d{2})\b', year_text)
                if found_years:
                    year=found_years[0]

    return year


def passport_date_extraction(string,input_date):
    input_date = parser.parse(input_date,yearfirst=True).date()
    # try:
    if int(string[0:2])>15:
        string='19'+string
    else:
        string='20'+string
    extracted_date = parser.parse(string, yearfirst=True).date()

    if extracted_date == input_date:
        return True
    else:
        return False


def match_id_dob(date_line, input_date):
    input_date = parser.parse(input_date)
    date_regex = re.findall(
        r'\b(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{4}|(?:Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\b',
        date_line)

    all_dates = []

    if date_regex:
        for date_string in date_regex:
            try:
                parsed_date = parser.parse(date_string)

                threshold_date=parser.parse('20/11/2013')
                if parsed_date < threshold_date:
                    if parsed_date.date()==input_date.date():
                        all_dates.append(True)
                    else:
                        all_dates.append(False)
            except:
                pass

    else:
        all_dates.append(False)

    date_status=any(all_dates)

    return date_status



def is_within_3_months(date_string: str) -> bool:
    try:
        # Parse the date string using dateutil's parser
        parsed_date = parser.parse(date_string)

        # Get the current date
        current_date = datetime.now()

        # Calculate the date 43 months ago from now
        months_delta = timedelta(days=3 * 30)  # Approximately 30 days per month
        threshold_date = current_date - months_delta

        # Check if the parsed date is within the last 43 months
        return parsed_date.date() >= threshold_date.date()

    except (ValueError, OverflowError) as e:
        # Handle invalid date strings
        print(f"Error parsing date '{date_string}': {e}")
        return False
