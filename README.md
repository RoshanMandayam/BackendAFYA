This project was created as part of a hackathon. I designed an API endpoint that scrapes medical provider data 
from the NPPES website so that users  can call the API with a specific address and it responds with the three closest
medical providers(given certain constraints).


Note: Data validation was started but could  not be finished due to time constraints! With more time, I would use additional
regular expressions to clean the address information so that it could be sent for geopy to search without error.


How to use API:
1. Clone the github repo
2. Download Docker (download the desktop app: https://www.docker.com/products/docker-desktop/)
3. Build the Docker Image using the terminal ( 'docker build -t nameOfYourImage .' ), after navigating to the current project folder
4. Run the container( 'docker run -p 8080:8080 -v /host/directory:/container/directory nameOfYourImage' ), changing the file paths accordingly (my example is /Users/roshanmandayam/BackendAFYA:/app)
5. Go to postman and create a workspace to test the API. There are two main calls you can make (GET  requests).
    a. By pasting 'http://127.0.0.1:8080/scrape' , you can call the function that scrapes the NPPES website and stores NPI numbers with 
        specialist details like Name, Address, Phone, and Specialty. BUT since the scraping function takes upwards of 15 minutes
        to go through all the reference NPI's, I have pre-fetched the data once and stored it (in 'specialists.json' ).


   b. You can find the closest 3 specialists to an address that you input by pasting
        http://127.0.0.1:8080/top_specialists?address="YOUR_ADDRESS" replacing YOUR_ADDRESS with one you'd like to test.
        Make sure to follow the format "1600 Amphitheatre Parkway, Mountain View, CA 94043"
        i.e. "number street, city, state zip"


How to read the output of the top_specialists GET request:

    1. It is in JSON form. The first entry, "Closest Match" tells you the address that the API endpoint used to calculate the nearest specialists.
    Note that if your address was unclear, the closest match may be an address that you did not intend.
    2. The second entry, 'status', tells you that it was successful. If it wasn't you will get an error message.
    3. The third entry, '0' or '1' or '2', tells you the rank by distance of the specialist. And inside each of these entries
        is another dictionary with the NPI and distance (a float). And inside of the NPI entry is more details regarding the
        specialist like name, address, etc.

**The dockerfile has the line CMD ["pytest"] commented out. Uncomment and replace the other cmd line if  you'd like to run the test_app.py file. Since I am low on time, I did very basic unit testing, but with a full length project much more tests and edge cases would be added.





