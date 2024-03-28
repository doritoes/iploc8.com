# Testing and Monitoring
Your site should be up and running (allow time for DNS propagation)

## Browser Testing
Point your Browser to your site to test each way the site can be accessed
- HTTP to the domain name (i.e., http://iploc8.com which should redirect to https)
- HTTPS to the domain name (i.e., https://iploc8.com)
- HTTP to the subdomain (i.e., http://www.iploc8.com which should redirect to https)
- HTTPS to the subdomain (i.e., https://www.iploc.com)

## nslookup
From a command line test both DNS lookups. For example:
- ```nslookup iploc8.com```
- ```nslookup www.iploc8.com```

## DNS global propagation
- Visit https://dnschecker.org/
- Enter your domain name and click Search
  - Examples:
    - https://dnschecker.org/#A/iploc8.com
    - https://dnschecker.org/#A/www.iploc8.com
   
## Monitoring
Feel free to experiment with CloudWatch (search for "CloudWatch" in the AWS console). Be aware that configuring monitoring will generate additional traffic (load).

Start with *view automatic dashboards* and work from there.

CloudWatch > Dashboards > Automatic dashboards
- Elastic Container Service

CloudWatch > Metrics > All Metrics
- ECS - View automatic dashboard
- ApplicationELB - View automatic dashboard
- CloudFront - View automatic dashboard
  - Request count
  - Error rates

CloudWatch > Logs > Log Groups > /ecs/iploc8-app
- search for events containing words like "scaling", "target tracking", or "capacity"
