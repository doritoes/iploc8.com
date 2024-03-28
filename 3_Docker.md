# Building Docker Container
Create and Build the Web App Container

Overview:
- Clone the application from Github
- Optionally customize the web application
- Build the image
- Test the image in Docker

## Clone the Repository
1. Open a command prompt
2. Change directory to where you want to create your project (i.e., `C:\docker`)
3. `git clone https://github.com/doritoes/iploc8.com`
4. Examine the new subdirectory `iploc8.com` (i.e., `c:\docker\iploc8.com`)
    - `app` directory contains the web application

## Customize the iploc8.com Flask App
Optionally, customize the application.

You will note that the application leverages (ip-api)[https://ip-api.com] for IP address lookup.

## Build the image
1. From the command line change directory for your project folder
    - i.e., `cd c:\docker\iploc8.com`
2. Build the image using
    - `docker build -t flask .`
    - Be sure you have the dot at the end; this means "the current directory"

## Test the image in Docker
1. Run the container locally:
    - `docker run -p 5000:5000 flask`
    - If Docker asks to if you want to permit the required network access, Accept it
2. Launch a browser and point to: http://127.0.0.1:5000
    - You are running the container on your local host, so the IP address is 127.0.0.1
    - The application port is 5000 and are mapping it to your host port 5000, hence the `:5000` at the end
    - open Docker Desktop, click on the running container, and click the Inspect tab then Networks to learn more
3. Try out some of the following links to the the container:
    - http://127.0.0.1:5000/
    - http://127.0.0.1:5000/healthcheck
    - http://127.0.0.1:5000/test.html
      - the client IP address is returned via the ipify.org service
      - the data is returned from iploc8.com
      - the API key is validated and the connection secured using JWT
        - first the API is posted to retrieve a token
        - second the data is retrieved, secured by the token
      - you can modify the url and apiKey to use your local docker container api v2
    - http://127.0.0.1:5000/api/v1/ip?ip=8.8.8.8
    - http://127.0.0.1:5000/api/v3/ip/8.8.8.8
    - http://127.0.0.1:5000/api/v4/ip/8.8.8.8
3. Back at the command line, press **Control-C** to stop the container
4. You can delete the container if you want, but keep the image as we will be pushing it to AWS ECR using in the next step

# Learn More
## Testing health check function
You can point your browser to the healtch check URL: http://127.0.0.1:5000/healthcheck

Another way is to use a `curl` command: `curl -v http://127.0.0.1:5000/healthcheck`

### Container up for longer that 12 hours
If the container us up longer that 12 hours, an HTTP 203 status will be retuns an a message explaining why.
~~~
{
  "status": "Container uptime exceeds threshold (uptime: 234027.9399881363 seconds)"
}
~~

### Empty tables in the database
If some of the external data fails to load in the MySQL database, an HTTP 500 status is returned.

Currently this is only tested at first boot-up.

### MySQL is down
If MySQL (mysqld) dies or hangs, an HTTP 500 status is returned.

How to simulate:
1. Use Docker Desktop "Exec" tab to get to command line in the container
2. Install procps tools
    - `microdnf install procps`
3. Kill the mysqld process
    - `pkill mysqld`

The health check will now return an HTTP 500 status.
~~~
{
  "error": "Database query failed"
}
~~~

## postman
Download [postman]([https://www.postman.com/](https://www.postman.com/downloads/)) or use the web version to test the API.

You don't need to create an account for basic features. We will point postman at our Docker container.

### Test api v1
1. Set the method to **GET**
2. Enter the url **http://localhost:5000/api/v1/ip?ip=9.9.9.9**
3. Click **Send**
4. See the data returned below

### Test api v3 and v4
1. Set the method to **GET**
2. Enter the url **http://localhost:5000/api/v3/ip/9.9.9.9**
3. Click **Send**
4. See the data returned below
5. Repeat for the url **http://localhost:5000/api/v3/ip/9.9.9.9**
6. Examine the results. Note the attribution information. This is not required for use for the data. However, I appreciate ip-api.com and want to provide this information in my API in support of their free service.

### Test api v2
This one is a bit more complex and secure. Examine the static `test.html` file to see how this same process is done using javascript.
1. Create the first tab to get the JWT token
    - Set the method to **POST**
    - URL: **http://localhost:5000/api/v2/login**
    - Headers: Add header **Content-Type** with value **application/json**
    - Body: click the **raw** tab and enter: `{ "api_key": "e95b186d-3677-4466-9cb2-20a549ab1d85" }`
      - if you changed the api key in your container, update this it match it
    - Click **Send**
    - Copy the "access_token" value from the response
    - We will use this access token in the next step
2. Create a second tab to get make queries against the API
    - Set the method to **POST**
    - URL: http://localhost:5000/api/v2/ip
    - Click the **Authorization** tab, and from the Type dropdown, select **Bearer Token**
      - Paste the token from the previous step into this field
    - Headers: add a header named **Content-Type** and the value **application/json**
    - Body:  click the **raw** tab and enter: `{ "ip": "9.9.9.9" }`
    - Click **Send**
3. Examine the results. Note the attribution information. The data is sources from a provider that requires displaying a link to their site.

## sqlmap
Since we are exposing an API with a SQL database to the internet, it is important to consider API security. We will be configuring the (expensive) AWS CloudFront WAP in front of the API later. However, this is an opportunity to get experience testing the security of the API with the sqlmap tool.

For information on installing sqlmap: https://github.com/sqlmapproject/sqlmap

Let's run it against our container:
- `python3 sqlmap.py http://127.0.0.1:5000/api/v1/ip?ip=8.8.8.8`
- `python3 sqlmap.py http://127.0.0.1:5000/api/v4/ip?ip=8.8.8.8`

It's not very exciting because if the strong input validation in the app.py file. The app returns HTTP 400 for invalid IP addresses. If you open Docker Desktop and look at the logs, it's very boring.

To view the logs from the commmand line
- docker ps
- docker logs <container ID from the previous command.

As an experiment you can strip out some of the input validation, build, and run. You will then see a whole lot of SQL injection attacks to attempt to access the database, dump data, and more.

BE SURE to restore the input validations BEFORE you deploy the container publicly.

## Checking for Vulnerabilities
You will be amazed how so simple an application can accumulate vulnerabilities.

In Docker Desktop, click in the Image that you built. On the right side, note the tabs "Images", "Vulnerabilities" and "Packages".

Note the 3 images used to build the image. Note how each image inherits the vunlerabilities of the image above and passes then on to the image below.

Images: Do any of the image have a newer image available?

Vulnerabilties: What packages are vulnerable? What layers (lines in the Dockerfile) introduce these vulnerabilities? If you expand the vulnerable librarites, note the CVE and CWE links. You can click those for more information.

In the top right find *Recommended fixes*. What recommendations do you find?

Common example for rebuilding with a new base image version:
`docker build --pull . -t flask:latest

Note that Docker Desktop has more extensions to help you examine your iamges:
- Anchore - no account required, scans all images for vulnerable packages
- Aqua Trivy - no account required
- Snyk - account required, limited personal user for free
- Lacework Scanner - requires a subscription

Ther are other vulnerability scanners for images outside of Docker desktop:
- Clar
- Snyk
- Trivy

## Learn about securing Docker Containers
https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

What are some secruity concerns with this the iploc8.com container?
- design prevents using --read-only filesystem
- what else?
