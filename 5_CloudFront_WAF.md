# Configuring CloudFront with WAF
The next step is to create the CloudFront distribution. This acts as a global content delivery network (CDN), caching API Gateway responses closer to end-users, reducing latency and improving the overall performance. We will not incur the cost of enabling the WAF (Web Application Firewall) as the app simply returns HTML. There is no API to protect. Another reason we are using CloudFront is that in later steps we will be adding more instances to additional AWS regions. CloudFront will distribute traffic to the nearest region (latency-based routing).

Additionally we will enable the CloudFront WAF to project our API. https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/distribution-web-awswaf.html

**THIS WILL COST YOU MONEY** - read more at
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/CloudFrontPricing.html
- https://aws.amazon.com/waf/pricing/

It is possible to configure health checks within CloudFront to automatically route traffic away from unhealthy regions should an issue arise. **IMPORTANT** - be mindful of potential cross-region data transfer costs when using multiple origins in different regions.

https://www.stormit.cloud/blog/cloudfront-distribution-for-amazon-ec2-alb/

## Log in to AWS Console and Navigate to CloudFront
1. Browse to (https://console.aws.amazon.com) and log in
2. In the search bar enter "CloudFront" and click on **CloudFront**
   
## Create a CloudFront Distribution
1. Click **Create a CloudFront distribution**
  - Origin name: *click in this box, and select your ALB from the list* (i.e., ipdice-alb-us-east-1)
  - Protocol: **HTTPS only** on port **443** with **TLSv1.2**
  - Origin path - optional: *leave blank* :!:
  - Name: *leave it as is, this is the domain name CloudFront will point to* (i.e., iploc8-alb-us-east-1-1200125694.us-east-1.elb.amazonaws.com)
  - Viewer > Viewer protocol policy: **Redirect HTTP to HTTPS**
  - Leave the remaining Origin settings at their default values
  - Default cache behavior leave at default values
  - Viewer
    - **Redirect HTTP to HTTPS**
    - Allowed HTTP methods: **GET, HEAD**
  - Caching (Important):
    - Choose **CachingOptimized**
    - Origin Request policy: (<ins>important</ins>)
      - **AllViewer**
    - Response headers policy - **NONE**
  - Web Application Firewall (WAF)
    - **Do not enable security protections**
    - Our function is not an API (just simple HTML) and doesn't need this expensive add-on
  - Settings
    - Price class: To reduce cost, set to **Use only North America and Europe**
    - Alternate domain name (CNAME) - optional
      - Click **Add item**
          - add the domain names you will use, see my examples
          - ipdice.com
          - www.ipdice.com
    - Custom SSL certificate - optional
      - From the drop-down select your new certificate
    - Default root object - **index.php** (if you have issues, change back to **/**)
    - Click **Create distribution**. Be patient as the deployment completes.
    - **TAKE NOTE** of the *distribution domain name* - you will need this (my example: https://dgfd3kx8wcc5x.cloudfront.net)
2. Click on the **Behaviors** tab and create some behaviors
    - /api/v1/*
      - path pattern /api/v1/*
      - iploc8-origin-group
      - redirect HTTP to HTTPS
      - GET, HEAD
      - Cache policy: CachingDisabled
      - Origin request policy: AllViewer
      - Response header policy: None
    - /api/v2/*
      - path pattern /api/v2/*
      - single origin only; can't select origin group because we need the POST method
      - redirect HTTP to HTTPS
      - GET, HEAD, OPTIONS, PUT, POST
      - Cache policy: CachingDisabled
      - Origin request policy: AllViewer
      - Response header policy: None
    - /api/v3/*
      - path pattern /api/v1/*
      - iploc8-origin-group
      - redirect HTTP to HTTPS
      - GET, HEAD
      - Cache policy: CachingDisabled
      - Origin request policy: AllViewer
      - Response header policy: **SimpleCORS**
        - This allows other web sites to use this API
    - /api/v4/*
      - path pattern /api/v1/*
      - iploc8-origin-group
      - redirect HTTP to HTTPS
      - GET, HEAD
      - Cache policy: CachingDisabled
      - Origin request policy: AllViewer
      - Response header policy: None
3. ⚠️ You cannot test browsing to the distribution domain

## Reconfigure Route 53
Modify your existing Route 53 "A" record for both "iploc8.com"
- Record type stays "**A**"
- Alias stays "**On**"
- Route traffic to: **Alias to CloudFront distribution**
- Region: **the region where your CloudFront distribution is located**
- *Select your distribution from the dropdown list*
- Routing policy: **Simple routing**
- Click **Save**

## Configure WAF
1. In the search bar enter "CloudFront" and click on **CloudFront**
2. Click on your distribution
3. Click on the **Security** tab then click **Edit**
    - Review the settings, then click **Cancel** or **Save changes**
4. To enable the *Rate limiting* protection, click the link that says *Monitor mode* and then click **Enable blocking**
5. Expand *CloudFront geographic restrictions* then click **Edit**
    - Review your options, then click **Cancel** or **Save changes**
6. Expand *Sampled bot requests for the specified time range* and click **Manage bot protection*
    - Review your options and the pricing concerns, then click **Cancel** or **Save changes**
7. Expand *Request logs from the specified time range* and consider the cost to enabling AWS WAF logs

## Test
Allow for DNS entries to propagate (e.g., https://dnschecker.org/#A/www.iploc8.com)

Test each variation:
- http://www.iploc8.com
- https://www.iploc8.com
- http://iploc8.com
- https://iploc8.com

The client IP address should be returned by the application.
