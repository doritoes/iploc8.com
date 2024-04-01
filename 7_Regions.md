# Adding Regions
Our test application https://www.iploc8.com is running just fine. How can we make it more globally accessible and performant?

*See https://aws.amazon.com/blogs/networking-and-content-delivery/latency-based-routing-leveraging-amazon-cloudfront-for-a-multi-region-active-active-architecture/*

In this example we are doing to use:
- us-east-1 (N. Virginia)
- us-west-2 (Oregon)

We are not going to deploy to eu-central-1 (Frankfurt) because
- Only two origins can be in a CloudFront origin group
- We are not going to set up latency-based Route 53 records to point to the ALBs in this case

## Steps
1. Create Secret for the Repository in the additional region
2. Create ECR repository in the additional region
3. Configure the AWI CLI for the additional region, tag & push the image to the ECR
4. Create VPC in the additional region
5. Create Security Groups (ECS and ALB) in the additional region
6. Create TLS certificate in the additional region
7. Create Application Load Balancer (ALB) in the additional region
8. Create ECS cluster in the additional region
9. Create Task Definition in the additional region
10. Create a Service in the additional region
11. Configure CloudFront to add the new origin in the additional region
12. Route 53 Setup

#### Configure CloudFront to add the origin
:warning: You can only have two origins in an origin group
1. Browse to (https://console.aws.amazon.com) and log in
2. In the search bar enter "cloudfront" and click on **CloudFront**
3. Click on your distribution (i.e., for iploc8.com, www.iploc8.com)
4. Click the **Origins** tab
5. Click **Create Origin**
    - Origin domain: *start typing and you will have a list to choose from* (i.e., iploc8-alb-us-west-2)
    - Origin path - optional: *leave blank*
    - Name:  *leave it as is, this is the domain name CloudFront will point to* (i.e., iploc8-alb-us-west-2-1531905465.us-west-2.elb.amazonaws.com)
    - Click **Create origin**
6. Click **Create origin group**
    - Origins: Select each origin and click **Add** (re-order as needed)
    - Name: **iploc8-origin-group**
    - Failover criteria (required)
      - 502
      - 503
      - 504
    - **Click Create origin group**
    - Edit Default behavior
      - Click **Behaviors** tab
      - Select the *Default* behavior and click **Edit**
      - Change Origin and origin groups to **iploc8-origin-group**
      - Click **Save** changes
    - Repeat for any remaining behaviors <ins>except</ins> /api/v2/* because it does not support origin groups

#### Route 53 Setup
We are not going to set up another DNS name to use latency-based routing to direct traffic to the ALBs. CloudFront will be our mechanism to distribute traffic.

### Testing
First, we will generate traffic sourced from different global regions, followed by confirming traffic is reaching all regions.

#### Generate traffic with Online Speed Test Tools
These have limited locations but can quickly generate traffic to your different regions.
- Pingdom: https://tools.pingdom.com/ (select from *Test from*)
- WebPageTest: https://www.webpagetest.org/ (advanced options let you select more locations)

#### Generate traffic with VPN Services
Use a VPN service (some have free options) that lets you connect through servers in various countries. In this way you can access the site from, say, Seattle.

#### Validating Regional ECS usage
Logs
1. In the search bar enter "CloudWatch" and click on **CloudWatch**
2. Select the region you want to see logs for from the region drop-down
3. From the left Menu, expand **Logs** and click **Log groups**
4. Click on the ecs log group (e.g., /ecs/iploc8-app-us-west-2)
5. Use region dropdown to confirm you have invocations in each region

Dashboard
1. In the search bar enter "CloudWatch" and click on **CloudWatch**
2. Select the region you want to see logs for from the region drop-down
3. From the left Menu click **Dashboards** > **Automatic dashboards**
4. Click **Application ELB**

⚠️ In initial testing with origins in two regions did not see the container logging any hits in us-west-2.

# Learning More
- Think about pricing model of CloudFront affects your ability to add your application to regions outside US and Europe
- What do you think the capacity for each container is at 0.5vPC and 1Gb of memory at 80% target CPU?
- What do you think the maximum capability of the max 10 scale size is?
- How can you increase the capacity of each container to support more traffic?
