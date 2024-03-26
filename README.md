Note: Data validation was started but could  not be finished due to time constraints! With more time, I would use additional
regular expressions to clean the address information so that it could be sent for geopy to search without error.


How to use API:
1. Clone the github repo
2. Replace the api keys for the Google Map API Key (line 74 of app.py, session['key'] = "YOUR_API_KEY")
3. Download Docker (download the desktop app: https://www.docker.com/products/docker-desktop/)
4. Build the Docker Image using the terminal ( 'docker build -t nameOfYourImage .' ), after navigating to the current project folder
5. Run the container( 'docker run -p 8080:8080 -v /host/directory:/container/directory nameOfYourImage' ), changing the file paths accordingly (my example is /Users/roshanmandayam/BackendAFYA:/app)
6. Go to postman and create a workspace to test the API. There are two main calls you can make (GET  requests).
    a. By pasting 'http://127.0.0.1:8080/scrape' , you can call the function that scrapes the NPPES website and stores NPI numbers with 
        specialist details like Name, Address, Phone, and Specialty. BUT since the scraping function takes upwards of 15 minutes
        to go through all the reference NPI's, I have pre-fetched the data once and stored it (in 'specialists.json' ).
    b. You can find the closest 3 specialists to an address that you input by pasting
        http://127.0.0.1:8080/top_specialists?address="YOUR_ADDRESS" replacing YOUR_ADDRESS with one you'd like to test.
        Make sure to follow the format "1600 Amphitheatre Parkway, Mountain View, CA 94043"
        i.e. "number street, city, state zip"





