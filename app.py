from flask import Flask, request, jsonify
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut
import re



app = Flask(__name__)
app.secret_key = "abcde2o38cniuwc"
app.app_context().push()

NPI_INFO = {}
with open('specialists.json', 'r') as file:
    data = json.load(file)

def read_csv_to_list(csv_file):
    data = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for index, row in enumerate(reader):
            if index % 2 == 1 or index==0 :  # Skip odd rows (indices are zero-based) and header row
                continue
            data.append(int(row[0]))
    return data

def get_coord(text_address):
    geolocator = Nominatim(user_agent="app",timeout = 10)
    try:
        coords = geolocator.geocode(text_address, limit = 3)
        if not coords:
            return None
        if len(coords) > 1:
            return None
    except GeocoderTimedOut:
        return None
    
    

    return {"latitude":coords.latitude,"longitude":coords.longitude}

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
            
            text_address = re.sub(r'(SUITE|STE) [A-Z]\d*', '', text_address)
            text_address = re.sub(r'(SUITE|STE) [A-Z]', '', text_address)
            text_address = re.sub(r'(SUITE|STE) \d+', '', text_address).strip() 
            text_address = re.sub(r'FL \d+', '', text_address)
            text_address = re.sub(r'RM \d+', '', text_address)
            text_address = re.sub(r'OFARRELL', "O'FARRELL", text_address)
            text_address = re.sub(r'SPC \d+', '', text_address)
            text_address = re.sub(r'LN \d+', '', text_address) 
            #More data cleaning and validation can be added, but were not added yet due to time constraint!
            
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



@app.route("/scrape", methods = ['GET'])
def scrape():

    csv_file = 'NPI_LIST.csv'  # Replace 'data.csv' with the path to your CSV file
    data = read_csv_to_list(csv_file)
    
    #scraping time
    for npi_index, npi in enumerate(data):
        #time.sleep(1)
        if  npi_index < 200:# or npi_index > 500: #60 to 100
            continue
        specialist_details = scrape_specialist_info(npi)
        if specialist_details == -1:
            continue
        else:
            NPI_INFO[npi] = specialist_details
    # File path
    file_path = "specialists.json"

    #Write data to JSON file
    with open(file_path, "w") as json_file:
        json.dump(NPI_INFO, json_file)
    
    return NPI_INFO

def _get_top_specialists(data: dict, reference_address: str, n: int) -> list[tuple[str, float]]:
    reference_coords = get_coord(reference_address)
    if reference_coords  is None:
        return -1 #indicating this was a bad address input
    all_distances = {}
    for npi_number in data:
        specialist_address = data[(npi_number)]["Coordinates"]
        if specialist_address is None:
            continue
        distance = get_geo_distance(specialist_address["latitude"], specialist_address["longitude"], reference_coords["latitude"],reference_coords["longitude"])
        all_distances[npi_number] = distance
    all_distances = sorted(all_distances.items(), key=lambda t: t[1])
    return all_distances[:n]

#This function will return a JSON file of the closest 3 specialists
@app.route('/top_specialists', methods=['GET'])
def get_top_specialists():
    
    reference_address = request.args.get('address') #this is the address passed in by user
    if not reference_address:
        return jsonify({'Error': 'Reference address is required'}), 400
    
    

    #calculating the closest 3 specialists
    num_top_specialists = 3
    top_n = _get_top_specialists(data, reference_address, num_top_specialists)
    if top_n == -1 :
        return "You inputted an invalid address or the Geocoding service timed out. Please try again."
    # displaying the closest 3 specialists
    json_data = {
        str(i):{top_n[i][0]: data[top_n[i][0]], "Distance": top_n[i][1]}
        for i in range(num_top_specialists)
    }

    # in the format---   position: {NPI : {specialist details like address, name,etc} , Distance: float in kilometers}
    response = {
        "status": "success",
        "top_specialists": json_data
    }

    return jsonify(response) 








#This has nothing on it, except a welcome message to confirm it works
@app.route("/", methods = ['GET'])
def index():
    return "Website is working! Now go test the endpoint."

#Ensures the flask web server will only be started if run directly.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
