from flask import Flask, request, jsonify
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests



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
        xpath_expression = "//*[contains(text(), 'Invalid NPI.')]"

        # Find the element by XPath
        element = driver.find_element(By.XPATH, xpath_expression)
        #save_details = driver.find_element(By.XPATH,'//span[@_ngcontent-lft-c23][@tabindex="0"]')
        #driver.quit()
        #return -1 #this is an invalid NPI id
        details = "Invalid npi"
    except NoSuchElementException:
        #if we find that specific npi, then return all his/her details to the scraping route
        #details:specialist name, address, contact details, and specialty
        
        details={"Name":"Rosh", "Address":"123 Church St", "Phone": "925-464-1982", "Specialty":"Podiatrist"}
    driver.quit()    

    return details

    



# Mock specialist data (replace with actual scraping logic)
SPECIALISTS = [
    {
        "name": "Dr. John Smith",
        "address": "123 Main St, City, State",
        "contact": "123-456-7890",
        "specialty": "Cardiology",
        "distance": 5.2,  # Distance from reference address (in miles)
        "rating": 4.5     # Specialist rating (optional)
    },
    {
        "name": "Dr. Sarah Johnson",
        "address": "456 Oak St, City, State",
        "contact": "987-654-3210",
        "specialty": "Dermatology",
        "distance": 3.8,
        "rating": 4.8
    },
    # Add more specialists as needed
]

NPI_INFO = {}

@app.route("/", methods = ['GET','POST'])
def index():
    return "Testing"

@app.route("/scrape", methods = ['GET','POST'])
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

    return NPI_INFO
    return data
    return jsonify({'testing':'successful'})


@app.route('/top_specialists', methods=['GET'])
def get_top_specialists():
    reference_address = request.args.get('address')
    if not reference_address:
        return jsonify({'error': 'Reference address is required'}), 400

    # Implement ranking algorithm here (for now, just return first 3 specialists)
    top_specialists = sorted(SPECIALISTS, key=lambda x: x['distance'])[:3]

    return jsonify(top_specialists)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
