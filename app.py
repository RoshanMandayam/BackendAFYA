from flask import Flask, request, jsonify
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import json
import time

app = Flask(__name__)
app.secret_key = "abcde2o38cniuwc"
app.app_context().push()

def read_csv_to_list(csv_file):
    data = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            if index % 2 == 1 or index==0 :  # Skip odd rows (indices are zero-based) and header row
                continue
            data.append(int(row[0]))
    return data


def scrape_specialist_info(npi_num):
    #Beautifulsoup methhod trial:


    # Fetch the HTML content of the webpage
    #url = "https://npiregistry.cms.hhs.gov/provider-view/"+str(npi_num)
    #response = requests.get(url)
    #html_content = response.text
    #print(html_content)
    # Parse the HTML content with Beautiful Soup
    #soup = BeautifulSoup(html_content, 'html.parser')
    #error_div = soup.find('div', class_='alert alert-danger')
    #print(error_div)
    #invalid_span = soup.find('span', {'_ngcontent-wmi-c23': True, 'tabindex': '0'})
    #print(invalid_span)
    # if error_div:
    #     error_message = error_div.get_text(strip=True)
    #     return "INVALID ENTRY"
    # else:
    #     #print("Error message not found.")  
    #     return "replace with details"  
    
    #Selenium method below:::
    chrome_options = Options()
     
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage') #will write to disk instead of temp memory
    driver = webdriver.Chrome(options=chrome_options)
    #driver.get("https://npiregistry.cms.hhs.gov/search")
    driver.get("https://npiregistry.cms.hhs.gov/provider-view/"+str(npi_num) )
    #input_element = driver.find_element(By.ID,"npiNumber")
    #input_element.send_keys(npi_num)
    #input_element.send_keys(Keys.ENTER)
    
    try:
        time.sleep(1)
        xpath_expression = "//*[contains(text(), 'Error:')]"
        element = driver.find_element(By.XPATH, xpath_expression)
        try:
            xpath_expression = "//*[contains(text(), 'Invalid NPI.')]"
            element = driver.find_element(By.XPATH, xpath_expression)
            details = "Invalid NPI"
            driver.quit()
            return details
        except:        
            try:
                xpath_expression = "//*[contains(text(), 'No matching records found.')]"
                element = driver.find_element(By.XPATH,xpath_expression)
                details = "No matching records found."
                driver.quit()
                return details
            except NoSuchElementException:
                details = "UNKNOWN ERROR"

        #save_details = driver.find_element(By.XPATH,'//span[@_ngcontent-lft-c23][@tabindex="0"]')
        #driver.quit()
        #return -1 #this is an invalid NPI id
        
    
    except NoSuchElementException:
        
        #if we find that specific npi, then return all his/her details to the scraping route
        #details:specialist name, address, contact details, and specialty
        time.sleep(1)
        #print(driver.page_source)
        try:
            #name = driver.find_element(By.XPATH,"//*[contains(@class, 'blockquote')]")
            name = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/blockquote/p[1]")
            text_name = name.get_attribute("textContent").strip()
            #print(text_content)
        except NoSuchElementException:
            text_name = "Uknown Name?"
        
        try:
            #name = driver.find_element(By.XPATH,"//*[contains(@class, 'blockquote')]")
            person_info = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span")# | /html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span/text()[2] | /html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span/text()[3]")
            #/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span/text()[2]
            #address = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span")
            text_to_parse = person_info.text
            text_to_parse = text_to_parse.split("Phone: ")
            text_address = text_to_parse[0].replace("\n", " ").strip()
            text_phone = text_to_parse[1].split("|")
            text_phone = text_phone[0].strip()


            specialty = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[11]/td[2]/table/tbody/tr/td[2]")
            text_specialty = specialty.get_attribute("textContent").strip()
            text_specialty = text_specialty.split("- ")
            text_specialty = text_specialty[1].strip()
            #address.get_attribute("text")
            #print(text_content)
        except NoSuchElementException:
            text_address = "Uknown Addy?"

        #addres= 
        #phone = 
        #specialty = 
        details={"Name":text_name, "Address":text_address, "Phone": text_phone, "Specialty":text_specialty}
    driver.quit()    

    return details



NPI_INFO = {}

@app.route("/", methods = ['GET'])
def index():
    return "Testing"

@app.route("/scrape", methods = ['GET'])
def scrape():

    csv_file = 'NPI_LIST.csv'  # Replace 'data.csv' with the path to your CSV file
    data = read_csv_to_list(csv_file)
    
    #scraping time
    for npi_index, npi in enumerate(data):
        if  npi_index > 10 and int(npi) != 3000:
            continue
        specialist_details = scrape_specialist_info(npi)
        if specialist_details == -1:
            continue
        else:
            NPI_INFO[npi] = specialist_details
    # File path
    file_path = "data.json"

    #Write data to JSON file
    with open(file_path, "w") as json_file:
        json.dump(NPI_INFO, json_file)
    
    return NPI_INFO



@app.route('/top_specialists', methods=['GET'])
def get_top_specialists():
    reference_address = request.args.get('address')
    if not reference_address:
        return jsonify({'Error': 'Reference address is required'}), 400
    
    # Extract the first three entries
    first_three_specialists = dict(list(NPI_INFO.items())[:3])

    # Convert the first three entries to JSON
    json_data = json.dumps(first_three_specialists)
    response = {
        "status": "success",
        "top_specialists": first_three_specialists
    }
    # Implement ranking algorithm here (for now, just return first 3 specialists)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
