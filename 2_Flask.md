# Flask Application Design
This demonstration flask application is designed to be portable application with some unique features.
1. Leverages publicly available datasets
2. Loads the latest dataset at container load
3. Use Python flask to deliver the lightweight API
4. Use MySQL as a simple volatile data cache instead of a centralized database
    - No Exposed MySQL Port: The connection string in app.py uses 'localhost' for secure database access
5. Container self-expires afer 12 hours (configurable) for a unique data self-refresh mechanism
6. Four (4) different API endpoints to demonstrate different technologies
    - v1: simplistic lookup of country, no attribution required
    - v2: adds api key and JWT tokens for security; requires attribution to data source
    - v3: simplistic based on ip-api.com free data, adding niche corporate cloud proxy data
    - v4: simplistic based on ip-api.com paid pro offering, adding niche corporate cloud proxy data

## Core files
### Dockerfile
The Dockerfile uses the standard MySQL image (running Oracle Linux) with additional Python libraries to build the application.

### requirements.txt
Contains the list of Python3 libraries required so pip3 can install them

### start.sh
The entrypoint for the container is start.sh. It does some interesting things.
1. MySQL is started in the background, where it self-configures using the provided `schema.sql` file
2. Wait until MySQL is ready
3. Downloads fresh data from external sources
4. Unpacks compressed data and turns JSON data into CSV data
5. Imports CSV data into MySQL tables
6. Starts the app.py flash application in the foreground

### app.py
This is the flash application. It contains a number of interesting *routes*.
1. **/** - the root route
    - returns the static index.html "home page"
2. **/favicon.ico**
    - returns ths favicon.ico graphic file
3. **/robots.txt**
    - returns the static robots.txt file
4. **healthcheck**
    - returns the health of the container
      - did the database tables load corrrectly?
      - is the MySSQL database responding?
      - has the containuer been up over 12 hours, and needs to be rebuild with fresh data?
5. **/test.html**
    - Tests the JWT api key/authentication mechanism using endpoint /api/v2/ip
6. **/api/v1/ip**
    - simplistic GET-based API to return data of the country and ASN realted to the IP address
    - sources data that does not require attribution
7. **/api/v2/ip**
    - secure API that uses API key(s) and JWT tokens to secure access to the data
    - provides more information like the city, state, and postcode
    - leverages data that requires attribution for using its data
8. **/api/v3/ip**
    - leverages the free api from ip-api.com to provide data with some custom enrichment
      - attempts to provide a respectful wrapper that backs off when the ip-api.com signals too many requests
8. **/api/v4/ip**
    - leverages a paid api key from ip-api.com to provide data with some custom enrichment
    - uses origin limitations on the api key to prevent abuse
  
9. **/api/v4/ip**
- startup Script (start.sh) : We manage MySQL initialization, schema loading, and Flask startup
- docker entrypoint support: Assumes your MySQL image uses /docker-entrypoint-initdb.d for initialization scripts
- adjust schema.sql, app.py (models, routes), and set your desired password

### schema.sql
Contains MySQL script to configure the database and table schemas.

### broadcom.py and zscaler.py
Scripts to download the cloud secure web gateway (SWG) ingress/egress networks of two popular corporate proxies and covert the data to CSV to ready insertion into the MySQL database

## Architecture
Built specifically to run on a serverless container environment. Runs MySQL and flask on same container to provide a way to do "just in time" data ingestion and service the results to the use.

Leverage container built-in services (e.g., Amazon ECS, EC2 load balancers) to keep the data auto-refreshing and modestly scale. Leverage AWS CloudFront CDN with the AWS WAF to protect the API.

# Notes
countries.csv was last refreshed from https://datahub.io/core/country-list on 3/19/2024
