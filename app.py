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
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re


app = Flask(__name__)
app.secret_key = "abcde2o38cniuwc"
app.app_context().push()

NPI_INFO = {}

def read_csv_to_list(csv_file):
    data = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            if index % 2 == 1 or index==0 :  # Skip odd rows (indices are zero-based) and header row
                continue
            data.append(int(row[0]))
    return data

#I MANUALLY REMOVED  PH 1 FROM GOSHEN AVE, 1012 from 6200 wilshsire blvd, and suite 215 from  16405 sand canyone ave
def get_coord(text_address):
    geolocator = Nominatim(user_agent="app",timeout = 10)
    #time.sleep(1)
    coords = geolocator.geocode(text_address)
    if not coords:
        print(f"Coords/location not found")
        return None

    return {"latitude":coords.latitude,"longitude":coords.longitude}
def get_geodesic_distance(address1, address2):
    geolocator = Nominatim(user_agent="my_app")
    
    # Get location (latitude and longitude) for address1
    location1 = geolocator.geocode(address1)
    if not location1:
        print(f"Location not found for address: {address1}")
        return None
    
    # Get location (latitude and longitude) for address2
    location2 = geolocator.geocode(address2)
    if not location2:
        print(f"Location not found for address: {address2}")
        return None
    
    # Calculate distance between two locations using geodesic distance
    distance = geodesic((location1.latitude, location1.longitude), (location2.latitude, location2.longitude)).kilometers
    
    return distance

def get_geo_distance(loc1lat,loc1long,loc2lat,loc2long):
    if loc1lat is None:
        return None
    if loc1long is None:
        return None
    # geolocator = Nominatim(user_agent="my_app")
    # loc1 = geolocator.geocode(address1)
    # if not loc1:
    #     print(f"Location not found for address: {address1}")
    #     return None
    
    distance = geodesic((loc1lat, loc1long), (loc2lat,loc2long)).kilometers
    return distance

def scrape_specialist_info(npi_num): 
    
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
            return -1
        except:        
            try:
                xpath_expression = "//*[contains(text(), 'No matching records found.')]"
                element = driver.find_element(By.XPATH,xpath_expression)
                details = "No matching records found."
                driver.quit()
                return -1
            except NoSuchElementException:
                details = "UNKNOWN ERROR"
                return -1
    
    except NoSuchElementException:
        
        #if we find that specific npi, then return all his/her details to the scraping route
        #details:specialist name, address, contact details, and specialty
        time.sleep(1)
        try:
            name = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/blockquote/p[1]")
            text_name = name.get_attribute("textContent").strip()
            
        except NoSuchElementException:
            text_name = "Uknown Name"
        
        try:
            person_info = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span")# | /html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span/text()[2] | /html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[7]/td[2]/span/text()[3]")
            text_to_parse = person_info.text
            text_to_parse = text_to_parse.split("Phone: ")
            replace = text_to_parse[0].find('\n')
            if replace != -1:
                text_to_parse[0] = text_to_parse[0][0:replace] + ', ' + text_to_parse[0][replace+1:]
            text_address = text_to_parse[0].replace("\n", " ").strip()
            extra_zip_code_portion = text_address.find('-')
            if extra_zip_code_portion != -1:
                text_address = text_address[0:extra_zip_code_portion]
            text_address = re.sub(r'SUITE \d+', '', text_address).strip() 
            text_address = re.sub(r'FL \d+', '', text_address)
            text_address = re.sub(r'STE \d+', '', text_address)
            text_address = re.sub(r'RM \d+', '', text_address)
            text_address = re.sub(r'OFARRELL', "O'FARRELL", text_address)
            text_phone = text_to_parse[1].split("|")
            text_phone = text_phone[0].strip()

            
            specialty = driver.find_element(By.XPATH,"/html/body/app-root/main/div/app-provider-view/div[3]/table/tbody/tr[11]/td[2]/table/tbody/tr/td[2]")
            text_specialty = specialty.get_attribute("textContent").strip()
            text_specialty = text_specialty.split("- ")
            text_specialty = text_specialty[1].strip()
            
        except NoSuchElementException:
            text_address = "Uknown Address"
        coord_address = get_coord(text_address)
        details={"Name":text_name, "Address":text_address, "Phone": text_phone, "Specialty":text_specialty, "Coordinates":coord_address}
    driver.quit()    

    return details


@app.route("/", methods = ['GET'])
def index():
    return "Website is up! Now go test the endpoint."

@app.route("/scrape", methods = ['GET'])
def scrape():

    csv_file = 'NPI_LIST.csv'  # Replace 'data.csv' with the path to your CSV file
    data = read_csv_to_list(csv_file)
    
    #scraping time
    for npi_index, npi in enumerate(data):
        #time.sleep(1)
        if  npi_index < 34 or npi_index > 40:
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


#"350 5th Ave, New York, NY"
@app.route('/top_specialists', methods=['GET'])
def get_top_specialists():
    reference_address = request.args.get('address')
    if not reference_address:
        return jsonify({'Error': 'Reference address is required'}), 400
    
    # Extract the first three entries
    #first_three_specialists = dict(list(NPI_INFO.items())[:3])
    first = [-1,float('inf')] #first -1 is for npi number, second float('inf') is for distance to inputted address. These should be replaced during the algorithm
    second= [-1,float('inf')]
    third = [-1,float('inf')]

    with open('data.json', 'r') as file:
        data = json.load(file)
        #print(data)
    
    address2 = get_coord(reference_address)
    for npi_number,provider_info in data.items():
        address1 = data[(npi_number)]["Coordinates"]
        #provider_info["Address"]
        if address1 is None:
            continue
        distance = get_geo_distance(address1["latitude"], address2["longitude"], address2["latitude"],address2["longitude"])
        
        if distance is not None:
            #print(distance)
            if distance <= first[1]:
                third[0] = second[0]
                third[1] = second[1]
                second[0] = first[0]
                second[1] = first[1]
                first[0] = npi_number
                first[1] = distance
            elif (distance <= second[1]):
                third[0] = second[0]
                third[1] = second[1]
                second[0] = npi_number
                second[1] = distance
            elif (distance  <= third[1]):
                third[0] = npi_number
                third[1] = distance
        
    # Convert the first three entries to JSON
    #json_data = json.dumps({data[first[0]],data[second[0]], data[third[0]]})
    json_data = {"First":data[first[0]],"Second":data[second[0]], "Third":data[third[0]]}
    response = {
        "status": "success",
        "top_specialists": json_data
    }
    # Implement ranking algorithm here (for now, just return first 3 specialists)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
