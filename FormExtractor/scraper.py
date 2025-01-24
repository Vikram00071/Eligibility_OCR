import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def website_automate(driver, cdr):
    """ Seaching on website with desired CDR number"""
    driver.get('https://brokercheck.finra.org/')
    time.sleep(6)
    name_div = driver.find_element(By.XPATH, '//input[@placeholder="Individual Name/CRD#"]')
    name_div.send_keys(str(cdr))
    search_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    search_button.click()
    time.sleep(5)


def data_extraction(driver):
    """ Check desired values in search result """
    broker_found = False
    investor_found = False
    status =False
    certification = False
    try:
        main_div = driver.find_element(By.XPATH,'//investor-tools-individual-search-result-template[@class="cursor-pointer h-full ng-star-inserted"]')

        try:
            main_div.find_element(By.XPATH, './/investor-tools-avatar[@class="text-broker-avatar"]')
            broker_found = True
        except:
            pass

        try:
            main_div.find_element(By.XPATH, './/investor-tools-avatar[@class="text-ia-avatar"]')
            investor_found = True
        except:
            pass

        main_div.click()
        time.sleep(5)

        all_results = driver.find_elements(By.XPATH, '//div[@class="flex-1 flex flex-row sm:flex-col"]')
        certificate_list = []
        for certificates in all_results:
            if ('Series 7' in certificates.text) or ('Series 82' in certificates.text) or (
                    'Series 65' in certificates.text):
                certificate_list.append(True)

        if any(certificate_list):
            certification = True



        if (broker_found or investor_found) and (certification):
            status = True
    except:
        pass

    return status

def licensed_individual( name,cdr_number):
    """function to check eligibility with Cdr number from website """
    income_status = scrap_from_website(cdr_number)
    return income_status


def scrap_from_website(cdr):
    """ Implementation of webdriver capabilities and getting results"""
    option = webdriver.ChromeOptions()
    option.add_argument("start-maximized")
    option.add_argument("headless")
    option.add_argument('log-level=1')
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--disable-blink-features=AutomationControlled')
    # option.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    website_automate(driver, cdr)
    time.sleep(4)
    status = data_extraction(driver)
    return status
