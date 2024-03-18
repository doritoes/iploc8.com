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

### Working on
- Bootstrapping repo on Github
### Will Do
- Bootstrapping image on Docker Hub
- Dummy API
- First geo API
- One region built
- Multi-region
- Add MS published address spaces
- Add Tor published address spaces
- Add Zscaler published POP addresses spaces
- Add Broadcom published POP addresses spaces
- Add OFAC flag
- Add ASN data
### Might Do
- Threat Intel enrichment
  - Proxy detection
  - Reputation/blacklists
  - 
- Might migrate to Azure or GCP if it becomes an interesting challenge
## Out of Scope
- Amazon Elastic Kubernetes Service (EKS) doesn't meet my criteria for integrating a new technology for me. I have done other Kubernetes labs ([here](https://www.unclenuc.com/lab:kubernetes_app:start) and [here](https://www.unclenuc.com/lab:stack_of_nucs:start)).

## Instructions
1. git clone https://github.com/doritoes/iploc8.com
2. cd iploc8.com
3. *set the MYSQL_ROOT_PASSWORD environment variable before building the image*
    - Windows: `set MYSQL_ROOT_PASSWORD=1a2d3m4i5n`
5. docker build -t my-flask-mysql .
6. docker run -p 5000:5000 -e MYSQL_ROOT_PASSWORD=your_password my-flask-mysql
7. Visit http://localhost:5000 to test the application
