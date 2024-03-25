# iploc8.com
Building a container-based geolocation API using Flask and MySQL running on Amazon ECS.

Why one container for Flash and MySQL? Isn't the current pattern to use docker compose with separate continers for each service?
* I wanted portable container that could easily run on ECS
* The container loads the most recent geo data at instantiation in the database for lookup, but not updates are made
* The container "ages out" after a configurable amount of runtime, trigging another container to load with fresh data

# Overview and Genesis
After building a few IP address look up sites on different technologies, I wanted to create my own custom geo-lookup API that I can leverage on my other sites.

The goal is to leverage repositories with geo-location data together with published IP address ranges to provide some unique perspective. There are many other API services that do enriched geo-location for a fee. However, the goal is this project is to develop the concept of what is possible independent of these services.

This demonstration site has the following features:
* Serverless computing on Fargate
* Small container based on Alpine Linux
* Python Flask with MySQL back-end database
* API design examples
  * unrestricted
  * JWT with API keys
  * CloudFront WAP protections
* Gradually release new experiences to the web application
* Demonstrate global autoscaling container applications without breaking the bank (don't want to cost too much for this free site)

# Project Goals
Here are the goals I have for this project. If you would like to encourage me to add additional goals or to complete these goals, I'm open to [contributions](https://account.venmo.com/u/unclenuc) to pay my Cloud bills.

## In Scope
### Completed
- Register domain name
- First geo API with country and ASN data
- Second geo API with city data, secured with API key and JWT tokens
- Add sanctions table
- favicon.ico
### Working on
- Bootstrapping repo on Github
- fix health check to work on a live table
- CORS testing
### Will Do
- bootstrapping image on Docker Hub
- one region built in ECS
- multi-region ECS
- Add MS published address spaces
- Add Tor published address spaces
- Add Zscaler published POP addresses spaces
- Add Broadcom published POP addresses spaces
- WAF API protection
### Might Do
- MS Azure customer space
- GCP customer space
- AWC customer space
- Proxy list ingest
- Threat Intel enrichment
  - Proxy detection
  - Reputation/blacklists
- Might migrate to Azure or GCP if it becomes an interesting challenge
## Out of Scope
- Amazon Elastic Kubernetes Service (EKS) doesn't meet my criteria for integrating a new technology for me. I have done other Kubernetes labs ([here](https://www.unclenuc.com/lab:kubernetes_app:start) and [here](https://www.unclenuc.com/lab:stack_of_nucs:start)).

# Quick Start
:warning: If you are using Windows, you need to do this in a WSL (Windows Subsystem for Linux) window. Otherwise, you will have line ending issues with the scripts and other text files.

1. git clone https://github.com/doritoes/iploc8.com
2. cd iploc8.com
3. docker build -t my-flask-mysql .
4. docker run -p 5000:5000 -e MYSQL_ROOT_PASSWORD=your_password my-flask-mysql
    - you will see "MySQL is unavailable -sleeping" for while
    - Or run detached: docker run -d -p 5000:5000 -e MYSQL_ROOT_PASSWORD=your_password flask
5. test
    - http://localhost:5000 - test page
    - http://localhost:5000/healthcheck - health check
    - http://localhost:5000/api/v1/ip?ip=67.248.106.77 - API v1
    - http://localhost:5000/test.html - API v2

# Step-by-Step
1. [Prerequistes](1_Prerequisites.md)
2. [Flask Application Design](2_Flask.md)
3. [Building Docker Container](3_Docker.md)
4. [Configuring ECS](4_ECS.md)
5. [Configuring CloudFront with WAF](5_CloudFront_WAF.md)
6. [Testing and Monitoring](6_Testing_and_Monitoring.md)
7. [Adding Regions](7_Regions.md)

# Data Sources
- https://datahub.io/core/country-list
  - countries.csv was last refreshed from here 3/19/2024
- https://github.com/sapics/ip-location-db
  - this data is loaded on each container initilization
## Find Out More
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
- Azure IP ranges and service tags - public cloud
  - https://www.microsoft.com/en-us/download/details.aspx?id=56519
- AWS EC2
  - https://docs.aws.amazon.com/vpc/latest/userguide/aws-ip-ranges.html
  - service is "EC2"
- https://www.abuseipdb.com/
- https://www.projecthoneypot.org/list_of_ips.php
- https://www.spamhaus.org/ip-reputation/
- https://status.fortisase.com/
