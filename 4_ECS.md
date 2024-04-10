# Configuring ECS
Here we will use Amazon Elastic Container Service (ECS) to host our container application. We will use Amazon Elastic Container Registry (ECR) to store and replicate the Docker image we built.

It is also important that we will be using the launch type **AWS Fargate**, a serverless model where AWS manages the underlying infrastructure for you. It's simpler but with less flexibility.

Tip: Make sure you are in the desired region (e.g., `us-east-1`)

*See https://aws.amazon.com/ecr/pricing/ for details about pricing after the first year of Free Tier*

*See https://medium.com/@h.fadili/amazon-elastic-container-service-ecs-with-a-load-balancer-67c9897cb70b*

## Create IAM User and Access Keys
1.  In the AWS console search bar enter "IAM" and click on **IAM**
2.  Click **Users** in the left sidebar
3.  Click **Add users** or **Create user** (click Next to proceed through each step)
    - User name: **ecs-admin**
    - Permissions options: **Attach policies directly**
    - Search and select the following policies:
      - **AmazonEC2ContainerRegistryFullAccess**: Gives full access to ECR actions.
      - **AmazonECS_FullAccess**: Provides permissions to interact with ECS.
      - **CloudWatchLogsFullAccess**: Grants permissions for logging (important for monitoring your application)
    - Click **Create user**
4. Click on the new user **ecs-admin**
5. Click **Security credentials**
6. Click **Create access key**
7. Use case: **Command Line Interface (CLI)**
    - check the confirmation box and click **Next**
8. Description: **ECS Administration**
9. Click **Create access key**
10. Click **Download .csv file**
    - Store this key securely!
    - Easy user can only have 2 active access keys at a time
    - This is your <ins>last chance to save</ins> information about the access key
11. Click **Done**

## Create Secret for the Repository
1. In the AWS console, search for "Secrets" and click on **Secrets Manager**
2. Click **Store a new secret**
3. Secret type: **Other type of secrets**
4. Key-value pairs: *use the information in the CSV file you downloaded*
    - Key: **username**
    - Value: *the access key ID from your ECR access keys*
    - Key: **password**
    - Value: *the secret access key from your ECR access keys*
5. Secret Name: **ecr-image-pull-credentials**
6. Description: **credentials for pulling images from ECR**
7. <ins>Do not configure automatic rotation</ins>
    - Once the application is up and running first try rotating the secret manually
    - Once you have successfully rotated the secret manually, look into enabling and configuration automatic rotation
8. Click **Store**
9. View the new secret *ecr-image-pull-credentials* and note the Secret ARN; you will need this later!

## Create an ECR Repository
1. In the search bar enter "ECR" and click on **Elastic Container Registry**
2. Click **Get Started** or **Create repository**
    - Visibility: **Private** (for image pulls)
    - Repository name: **iploc8**
    - Leave the rest at defaults
2. Click **Create repository**

## Configure the AWS CLI
1. Open a command line where we will use the AWS CLI
2. Authenticate and provide your AWS access keys
    - `aws configure`
    - Copy the access key ID from the CSV file you downloaded
    - Copy the secret access key from the CSV file you downloaded
    - Default region name: *your region* (e.g., us-east-1)
    - Default output formation: **json**

## Push Image
### Get ECR Login and Docker Working
This step authenticates the Docker client with Amazon ECR. It generates a temporary token (12 hours). It provides seamless Docker Login. The URL of your ECR repository is used for the last part. If the command fails, launch Docker Desktop to ensure the Docker Engine is running.
~~~
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin https://<your-account-id>.dkr.ecr.<your-region>.amazonaws.com
~~~
Confirm authentication worked: `aws ecr describe-images --repository-name iploc8`

### Tag Image
1. List images: `docker images`
2. Tag image
    - `docker tag flask <your_repository_url>:latest`
    - no "https" in the tag
3. Confirm: `docker images`
### Push Image
1. Push: `docker push <your_repository_url>:latest`
2. Confirm: `aws ecr describe-images --repository-name iploc8`

## Create VPC(s)
You need to configure VPCs for the networking in each region. The following example uses the `us-east-1` region.
1. In the AWS console search for "VPC" and click **VPC**
2. Click **Start VPC Wizard** or **Create VPC**
    - Resources: **VPC and more**
    - Most settings can be left at default
    - Name tag auto-generation: **iploc8**
    - Number of availability zones: **2**
    - Number of public subnets: **2**
    - Number of private subnets: **0**
    - NAT gateways: **None**
    - VPC Endpoints: **None** (S3 Gateway endpoints offer optimization but can add complexity for initial setup)
    - DNS: Enable both options, **DNS hostnames** and **DNS resolution**
    - Click **Create VPC**

## Create Security Groups
### Create Security Group for ECS
1. In the AWS console search for "EC2" and click **EC2**
2. From the left menu click **Network & Security** > **Security Groups**
3. Click **Create security group**
    - Name: **iploc8-ecs-sg**
    - Description: **Security group for access to ECS containers**
    - VPC: *select the VPC you created*
    - Inbound rules
      - Click **Add rule**
      - Type: **All traffic**
      - Protocol: *automatically All*
      - Port Range: *automatically All*
      - Source: **Anywhere-IPv4** (0.0.0.0/0)
    - Outbound rules: *Leave at default settings*
    - Click **Create security group**
      
### Create Security Group for Application Load Balancer
1. In the AWS console search for "EC2" and click **EC2**
2. From the left menu click **Network & Security** > **Security Groups**
3. Click **Create security group**
    - Name: **iploc8-alb-sg**
    - Description: **Security group for the Application Load Balancer**
    - VPC: *select the VPC you created*
    - Inbound rules
      - Click **Add rule**
        - Type: **HTTPS**
        - Protocol: *automatically TCP*
        - Port Range: *automatically 443*
        - Source: **Anywhere-IPv4** (0.0.0.0/0)
      - Click **Add rule**
        - Type: **HTTP**
        - Protocol: *automatically TCP*
        - Port Range: *automatically 80*
        - Source: **Anywhere-IPv4** (0.0.0.0/0)
    - Outbound rules: *Leave at default settings*
    - Click **Create security group**

## Create TLS Certificate using AWS Certificate Manager (ACM)
1. In the AWS console search for "Certificate" and click **Certificate Manager**
2. Click **Request**
    - Request a public certificate is selected
    - Click **Next**
    - Fully qualified domain name (see my example below, including the www subdomain)
      - iploc8.com
      - www.iploc8.com (used the *Add another name to this certificate* button)
    - Validation method: **DNS validation**
    - Key algorithm: RSA 2048
    - Click **Request**
3. Refresh the list of certificates until your new request is listed, *Pending validation*
4. Click on the request ID for the new certificate
5. Click **Create records in Route 53**, then click **Create records**
6. Refresh the list of certificates until the new certificate is validated and the status changes to *Issued*

## Create Application Load Balancer (ALB)
1. In the AWS console search for "EC2" and click **EC2**
2. From then left menu, under *Load Balancing* click **Load Balancers**
3. Click **Create load balancer**
4. Click **Create** under *Application Load Balancer*
    - Load balancer name: **iploc8-alb-us-east-1**
    - Scheme: **internet-facing**
    - IP address type: **IPv4**
    - VPC: *select the VPC you created earlier* (e.g., iploc8-vpc-us-east-1)
    - Mappings: select two availability zones; the public subnets will be automatically populated
    - Security groups
      - From the dropdown select the Security group you created for the load balancer (i.e., `iploc8-alb-sg`) (and <ins>only</ins> this security group)
    - Listeners and routing
      - Modify the protocol to **HTTPS**
      - Click the link **Create target group**
        - Target type: **IP addresses**
        - Target Group Name: **iploc8-target-group**
        - Protocol: **HTTP**
        - Port: **5000** (the port the container listens on)
        - IP address type: **IPv4**
        - VPC: *select the VPC you created*
        - Protocol version: **HTTP1**
        - Health Checks
          - Health check protocol: **HTTP**
          - Health check path: **/healthcheck**
          - Expand *Advanced health check settings* and review the options available
        - Register targets - *no targets right now; ECS tasks will be registered later*
        - Click **Create target group**
      - Back on the **Create Application Load Balancer** page
        - Under *Listeners and routing* click the refresh button
        - Select the new target group you created from the drop down
    - Security policy
      - Security category: **All security policies**
      - Policy name: *use the recommended option from the dropdown*
    - Default SSL/TLS server certificate
      - **From ACM**
      - Select the ACM certificate from the dropdown
    - AWS Web Application Firewall (WAF)
      - Check **Include WAF security protections behind the load balancer**
      - NOTE This incurs additional costs
      - The default auto-create ACL and action of *Block* are fine
    - Leave the remaining settings at defaults
    - **Click Create load balancer**
    - Add another listener to the Load Balancer
      - Click the load balancer then in the lower pane click on the tab **Listeners and rules**
      - Click **Add listener**
        - Protocol: **HTTP**
        - Port **80**
        - Select **Redirect to URL**
          - **URI parts**
          - **HTTPS**
          - **Port 443**
          - Status code **301 - Permanently moved**
      - Click **Add**

## Create an ECS Cluster
1.  In the AWS console search bar enter "ECS" and click on **Elastic Container Service**
2.  Click **Create cluster**
3.  Cluster name: **iploc8-cluster**
4.  Infrastructure: **AWS Fargate (serverless)**
5.  Click **Create**

## Create Role ecsTaskExecutionRole
This role allows ECS tasks to pull images from ECR and perform other necessary AWS actions.

1. In another browser tab, open the AWS console and navigate to **IAM**
2. Click **Roles**
3. Search for *ecsTaskExecutionRole*
4. If it does not exist
    - Click **Create role**
    - Type: **AWS service**
    - Use case: **Elastic Container Service** > **Elastic Container Service Task** (ECS tasks will use role)
    - Click **Next**
    - Search for the **AmazonECSTaskExecutionRolePolicy** policy and check the box next to it. This is a managed policy by AWS with the appropriate permissions.
    - Click **Next**
    - Role name: **ecsTaskExecutionRole**
    - Description: *Allows ECS tasks to call AWS services on your behalf*
    - Click **Create role**

## Define a Task Definition
1. Switch back to the ECS console, the window with your cluster `iploc8-cluster`
2. Click **Task Definition** > **Create new task definition** from the left menu (not with JSON)
    - Task definition family: **iploc8-app**
    - Launch type: **AWS Fargate**
    - OS, Architecture, Network mode: **Linux/X86_64**
    - Network mode: automatically set to *awsvpc* for Fargate
    - CPU: **0.5 vCPU**
    - Memory: **1 GB**
    - Task Role - grants your task's containers permissions to call other AWS services on your behalf (e.g., accessing an S3 bucket, sending a message to SNS) - **Leave Blank for Now**
    - Task Execution role - gives the ECS agent (running on the Fargate infrastructure) permissions to manage your tasks. It needs permissions like pulling container images from ECR and writing logs to CloudWatch - **ecsTaskExecutionRole**
    - Container - 1
      - Name: **iploc8-container**
      - Image URI: *your image URI* (copy this from ECR)
      - Essential container: **Yes**
      - Private registry authentication: **No**
      - Port Mappings
        - Container port: **5000** (our application listens on port 5000)
        - Protocol: **TCP**
        - Port name: *leave blank*
        - App protocol: **HTTP**
      - Read only root file system: **Leave off** (our application can run with Read Only enabled)
      - Resource allocation limits
        - Generally leave this as is. Note this is empty (no values)
      - Expand *Environment variables*
        - Click **Add environment variable**
        - Key: **MYSQL_ROOT_PASSWORD**
        - Value type: **Value**
        - Value: **your_password** (or specify your own value)
      - Log collection: **On** for testing, **Off** to reduce costs
      - HealthCheck - Optional: (incurs small costs)
        - Command: `CMD-SHELL,curl -f http://localhost:5000/healthcheck || exit 1`
        - Interval: **30** seconds (recommended)
        - Timeout: **5** seconds (recommended)
        - Start period: **300** seconds
          - This container by design takes a long time to start up. It downloads and imports data files from external sources. Without this change, the container will be terminated before it has a chance to come up and show "healthy".
        - Retries: **2** (one or two retries before making the container unhealthy)
    - Click **Create**

## Create a Service
1. Back in the ECS console, go to your cluster `iploc8-cluster`
2. In the lower pane, find the **Services** tab (probably already selected)
3. Click **Create**
    - Cluster: **iploc8-cluster**
    - Compute options: **Launch type**
      - Fargate
    - Application type: **Service**
    - Family: **iploc8-app** (from dropdown)
    - Revision: *LATEST*
    - Service name: **iploc8-service**
    - Service type: **Replica**
    - Desired tasks: **1** (start with 1 for initial testing; can scale later)
    - Deployment options > Deployment type: **Rolling updates** (default)
      - After you have the lab up and running, you can experiment with the Blue/green deployment type, which uses AWS CodeDeploy
    - Networking
      - VPC: **iploc8-ecs-sg**
      - The two subnets, one for each availability zone, should be listed
      - Security group: *Select the SG you created for ECS (only)* (i.e., iploc8-ecs-sg)
      - From the dropdown select the Security group you created for the load balancer (i.e., `iploc8-ecs-sg`)
      - Public IP: **ON**
      - Load balancing
        - Type: **Application Load Balancer**
        - Container: **iploc8-container 5000:5000** (from the dropdown)
        - **Use an existing load balancer**
        - Load balancer name: **iploc8-alb-us-east-1**
      - Listener
        - **Use an existing listener**
        - **443:HTTPS**
      - Target group
        - **Use an existing target group**
        - Target group name: *select from the dropdown* (i.e., iploc8-target-group)
    - Service auto scaling
      - Select **Use service auto scaling**
        - Minimum number of tasks: **1**
        - Maximum number of tasks: **10**
      - Click **Add scaling policies**
        - Type: **Target tracking**
        - Policy name: **iploc8-scaling-policy**
        - ECS service metric: **ECSServiceAverageCPUUtilization**
        - Target value: 80
        - Scale-out cooldown period: **300**
        - Scale-in cooldown period: **300**
      - Click **Create**
4. Click on the new service you created, then click **Update service**
    - Under Load balancing set *Health check grace period* to **240** seconds
    - This container by design takes a long time to start up. It downloads and imports data files from external sources. Without this change, the container will be terminated before it has a chance to come up and show "healthy".
    - Check **Force new deployment**
    - Click **Update**
5. Click the refresh buttons and look for
    - The cluster to show active, Active 1, Running 1
    - The service section will show the container health and status
    - If the status running but the status is *Unhealthy*, check your health check settings

## Test the container
Test the service public IP address (test directly to the container, who's IP address will keep changing)
1. ECS > Click your cluster > click your service > click tab tasks, click the first task > find the public IP
2. `http://<publicIP>:5000` (yes you need to add the port 5000, which the container listens on)
3. Page will load and show your IP address

Test ALB
1. EC2 > Load Balancers > Copy the DNS name (e.g., iploc8-alb-us-eat-1-1200125694.us-east-1.elb.amazonaws.com)
2. Try accessing by http and https
    - the certificate will not match until we configure Route 53

## Configure Route 53
1.  In the AWS console search bar enter "Route" and click on **Route 53**
2.  Click **Hosted Zones** and then the hosted zone that manages your domain (i.e., `iploc8.com`)
3.  Create A Records
    - No subdomain (i.e., `iploc8.com`)
      - Record type: **A**
      - Alias: **ON**
      - Route traffic to:
        - Alias Target: **Alias to Application and Classic Load Balancer**
        - Region: *Select the region where your ALB is located (e.g., "US East (N. Virginia)")*
        - Load balancer: *choose your load balancer from the list
        - Routing policy: **Latency**
        - Region: *Select the region where your ALB is located (e.g., "US East (N. Virginia)")*
      - Evaluate target health: **NO**
      - Record ID: **root-record**
    - The www subdomain (i.e., `www.iploc8.com`)
      - Record type: **A**
      - Alias: **ON**
      - Route traffic to:
        - Alias Target: **Alias to Application and Classic Load Balancer**
        - Region: Select the region where your ALB is located (e.g., "US East (N. Virginia)").
        - Load balancer: *choose your load balancer from the list
        - Routing policy: **Latency**
      - Evaluate target health: **NO**
      - Record ID: **www-record**

## Test
Here are some tests you can try to confirm the site is loading in all use cases
1. http://iploc8.com
2. https://iploc8.com
3. http://www.iploc8.com
4. https://www.iploc8.com

# Learn More
## ECR Image Scanning
In ECR you can select an image and click **Scan**. After a few minutes, you will have a report of vulnerabilities.

This report is significantly different from the output of your Docker Desktop vulnerability report. Interestingly, ELSA numbers are listed for our container, which links to the Oracle Linux Errata repository.
