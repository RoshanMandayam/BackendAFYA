# Use an official Python runtime as a parent image
FROM python:3.9.2

# Install wget utility
RUN apt-get update && apt-get install -y wget

# Install Chrome 
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver  123.0.6312.58 
RUN wget -q -O /tmp/chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.58/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip


ENV DISPLAY=:99
RUN Xvfb :99 -screen 0 1024x768x24 &

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

COPY . .
#ENV FLASK_APP=my_flask.py

EXPOSE 8080

# Run app.py when the container launches
CMD ["python", "app.py","--host", "0.0.0.0"]
#CMD ["pytest"]
#CMD ["Xvfb", ":99", "-screen", "0", "1024x768x24", "&", "your_chrome_command_here"]

#4. Build the Docker Image using the terminal ( 'docker build -t backend .' ), after navigating to the current project folder
#5. Run the container( 'docker run -p 8080:8080 -v /Users/roshanmandayam/BackendAFYA:/app backend' ), changing the file paths accordingly (my example is /Users/roshanmandayam/are-we-there-yet:/app) 
#i.e. "docker run -p 8080:8080 -v /Users/roshanmandayam/are-we-there-yet:/app flaskapp"