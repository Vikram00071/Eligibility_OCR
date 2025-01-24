
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def website_automate(driver,name,address):
    """ Seaching on website with desired CDR number"""
    driver.get("https://sanctionslist.ofac.treas.gov/Home/index.html")
    time.sleep(6)
    # Fill in the Name
    name_field = driver.find_element(By.ID, "input-type-name")
    name_field.send_keys(name)  # Replace with dynamic data

    # Fill in the Address (if needed)
    address_field = driver.find_element(By.ID, "input-type-address")
    address_field.send_keys(address)  # Replace with dynamic data

    # Click the Search button
    search_button = driver.find_element(By.CLASS_NAME, "usa-button")
    search_button.click()

    time.sleep(5)  # Wait for results to load
    # Check for results
    results = driver.find_elements(By.CSS_SELECTOR, "#searchTable tbody tr")
    if results:
        response=False
    else:
        response=True

    return response




def scrap_from_ofac_website(name,address):
    """ Implementation of webdriver capabilities and getting results"""
    option = webdriver.ChromeOptions()
    option.add_argument("start-maximized")
    # option.add_argument("headless")
    option.add_argument('log-level=1')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--disable-blink-features=AutomationControlled')
    # option.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    ofac_response=website_automate(driver,name,address)
    time.sleep(4)
    return ofac_response

