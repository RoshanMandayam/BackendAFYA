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


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Run app.py when the container launches
CMD ["python", "app.py","--host", "0.0.0.0"]
#CMD ["pytest"]
