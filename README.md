# iploc8.com
Building a container-based geolocation API using Flask and MySQL running on Amazon ECS.

# Overview and Genesis
After building a few IP address look up sites on different technologies, I wanted to create my own custom geo-lookup API that I can leverage on my other sites.

The goal is to leverage repositories with geo-location data together with published IP address ranges to provide some unique perspective. There are many other API services that do enriched geo-location for a fee. However, the goal is this project is to develop the concept of what is possible independent of these services.

This demonstration site has the following features:
* Small container based on Alpine Linux
* Python Flask with MySQL back-end database
* Serverless computing on Fargate
* Gradually release new experiences to the web application
* Demonstrate global autoscaling container applications without breaking the bank (don't want to cost too much for this free site)

# Project Goals
Here are the goals I have for this project. If you would like to encourage me to add additional goals or to complete these goals, I'm open to [contributions](https://account.venmo.com/u/unclenuc) to pay my Cloud bills.

## In Scope
### Completed
- Register domain name
- First geo API with country and ASN data
- Add sanctions table
- favicon.ico
### Working on
- Bootstrapping repo on Github
### Will Do
- fix health check to work on a live table
- clean up csv files after import
- Bootstrapping image on Docker Hub
- One region built
- Multi-region
- Add MS published address spaces
- Add Tor published address spaces
- Add Zscaler published POP addresses spaces
- Add Broadcom published POP addresses spaces
- Add ASN data
- WAF API protection
### Might Do
- MS Azure customer space
- GCP customer space
- AWC customer space
- Proxy list ingest
- Threat Intel enrichment
  - Proxy detection
  - Reputation/blacklists
- 
- Might migrate to Azure or GCP if it becomes an interesting challenge
## Out of Scope
- Amazon Elastic Kubernetes Service (EKS) doesn't meet my criteria for integrating a new technology for me. I have done other Kubernetes labs ([here](https://www.unclenuc.com/lab:kubernetes_app:start) and [here](https://www.unclenuc.com/lab:stack_of_nucs:start)).

# Instructions
:warning: If you are using Windows, you need to do this in a WSL (Windows Subsystem for Linux) window. Otherwise, you will have line-ending issues with the scripts and other text files.

1. git clone https://github.com/doritoes/iploc8.com
2. cd iploc8.com
3. *set the MYSQL_ROOT_PASSWORD environment variable before building the image*
    - Windows: `set MYSQL_ROOT_PASSWORD=1a2d3m4i5n`
4. docker build -t my-flask-mysql .
5. docker run -p 5000:5000 -e MYSQL_ROOT_PASSWORD=your_password my-flask-mysql
    - you will see "MySQL is unavailable -sleeping" for while
    - ERROR: it never progresses at this point
6. Visit http://localhost:5000 to test the application

Important notes
- No Exposed MySQL Port: The connection string in app.py uses 'localhost' for secure database access
- startup Script (start.sh) : We manage MySQL initialization, schema loading, and Flask startup
- docker entrypoint support: Assumes your MySQL image uses /docker-entrypoint-initdb.d for initialization scripts
- adjust schema.sql, app.py (models, routes), and set your desired password
- countries.csv was last refreshed from https://datahub.io/core/country-list on 3/19/2024

# Data Sources
- https://github.com/sapics/ip-location-db
- https://iptoasn.com/
- https://learn.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide
  - https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7
- Micorosoft Public IP address ranges in CSV https://www.microsoft.com/en-us/download/details.aspx?id=53602
- Broadcom proxy SWG
  - https://knowledge.broadcom.com/external/article/167174/web-security-service-wss-ingress-and-egr.html
  - https://servicepoints.threatpulse.com/
- Zscaler proxy SWG
  - https://config.zscaler.com/zscaler.net/cenr
    - https://config.zscaler.com/api/zscaler.net/cenr/json
  - https://config.zscaler.com/zscaler.net/hubs
    - https://config.zscaler.com/api/zscaler.net/hubs/cidr/json/recommended
- https://github.com/TheSpeedX/PROXY-List
- TOR exit nodes
