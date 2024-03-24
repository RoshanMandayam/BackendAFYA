from flask import Flask, request, jsonify
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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


def scrape_specialist_info():
    chrome_options = Options()
     
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage') #will write to diks instead of temp memory

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://npiregistry.cms.hhs.gov/search")
    input_element = driver.find_element(By.ID,"npiNumber")
    input_element.send_keys("Your text here")



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
    scrape_specialist_info()

    #scraping time
    for npi_index, npi in enumerate(data):
        continue

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
