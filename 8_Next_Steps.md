# Next Steps

## Deploy updated container image
You will need to repeat this for each region you are deployed in.

Rebuild the container (see [section 3](3_Docker.md) with the `--pull` argument. This requests docker to pull a fresh upstream image. This ensures you get the latest updates.

`docker build -t flask . --pull`

### Push the latest container to ECR
See [section 4](4_ECS.md) for the instructions for pushing images to ECR

### Update Task Definition
Is it a new image URI and/or a new tag? If so, do this:
1. In the AWS console search bar enter "ECS" and click **Elastic Container Service**
2. From the left menu click **Task definitions**
3. Click on your task (e.g. iploc8-app)
4. Click on the active revision (e.g., iploc8-app:5)
5. In the container definition section of new revision, update the image URI to point to your newly uploaded image in ECR (including the new tag)
6. Click **Create** to save the new revision

### Update Services
1. In the AWS console search bar enter "ECS" and click **Elastic Container Service**
2. Click **Clusters** then click your cluster (i.e., iploc8-cluster)
3. In the lower pane click **Services**
4. <ins>Select</ins> your service (i.e. iploc8-service) and click **Update**
5. Is this a new image URI and/or new tag?
    - YES: Select the new revision
    - NO: Check <ins>Force new deployment</ins>
6. Click **Update**

### Confirm
1. Watch the deployment progress to complete (new task spun up, old task spun down)
2. Click on the new task, find the Public IP and open it with port 8080 (e.g. http://3.81.118.133:5000)

## Reducing Costs
This is an expensive lab to run. Be sure to decomission it as soon as you are done with it.

Top costs:
* Public IP addresses
* ELB
* ECS
* WAF (⚠️there are costs per ACL that accumulate quickly)

### Remove unecessary public IP addresses
Amazon now charges about $3.60/month for public IP addresses. You don't need a public IP on the Load Balancer if you are using Route53 and CloudFront.

### Turn off logging
Turn off logging after the application is working, if you don't need the logs.
1. In the AWS console search bar enter "ECS" and click **Elastic Container Service**
2. From the left menu click **Task definitions**
3. Click on your Task definition
4. Click on the active Revision
5. Click **Create new revision** > **Create new revision** 
6. *Under Logging - optional* find *Log collection*
7. <ins>Uncheck</ins> **Use log collection**
8. Under container-1 find Log collection and turn it **Off**
9. Click **Create**
10. From the left menu click **Clusters** then click your cluster (i.e., iploc8-cluster)
11. In the lower pane click **Services**
12. <ins>Select</ins> your service (i.e. iploc8-service) and click **Update**
13. Revision: *select the new revision from the dropdown*
14. Click **Update**

### Reduce HealthCheck frequency
You can cut the HealthCheck traffic in half by doubling the timer.

1. In the AWS console search bar enter "ECS" and click **Elastic Container Service**
2. From the left menu click **Task definitions**
3. Click on your Task definition
4. Click on the active Revision
5. Click **Create new revision** > **Create new revision** 
6. *Under HealthCheck - optional* find *HealthCheck*
7. Interval: *increase this interval* (e.g., change from 30 seconds to 60 seconds)
8. Click **Create**
9. From the left menu click **Clusters** then click your cluster (i.e., iploc8-cluster)
10. In the lower pane click **Services**
11. <ins>Select</ins> your service (i.e. iploc8-service) and click **Update**
12. Revision: *select the new revision from the dropdown*
13. Click **Update**

### Turn off HealthCheck
Turning off HealthCheck reduces traffic to your container at the cost of a) losing auto-restarts for unhealthy containers and b) waiting until the container is healthy prior to sending traffic

1. In the AWS console search bar enter "ECS" and click **Elastic Container Service**
2. From the left menu click **Task definitions**
3. Click on your Task definition
4. Click on the active Revision
5. Click **Create new revision** > **Create new revision** 
6. *Under HealthCheck - optional* find *HealthCheck*
7. Command: **delete the health check command and make it blank**
8. Click **Create**
9. From the left menu click **Clusters** then click your cluster (i.e., iploc8-cluster)
10. In the lower pane click **Services**
11. <ins>Select</ins> your service (i.e. iploc8-service) and click **Update**
12. Revision: *select the new revision from the dropdown*
13. Click **Update**

## Invalidating CloudFront Cache Data (clearing the cache)
If you have deployed a new version of your application, sometimes you want to clear the cached data from CloudFront.

For example, if you updated one of the files in the `static` directory.

### Using AWS console
1. In the AWS console search bar enter "cloudfront" and click **CloudFront**
1. Click on your distribution
2. Click on the **Invalidations** tab
3. Click **Create invalidation**
4. Object paths: *enter everything you want to clear*
    - For example, to clear everything use **/***
5. Click **Create invalidation**
6. The status will go from *In progress* to *Completed*
    - The invalidation process might take some time depending on the size of your distribution and cache

### Using AWS CLI
1. Look up your distribution ID
2. `aws cloudfront create-invalidation --distribution-id <DistributionId> --paths "/*"`

## Learnings
In this lab you were introduced to Amazon ECS on Fargate, a serverless computing platform based on containers. You got to experiment with CloudFront and Route53.

I hope you take some time to look at the Python flask application itself, is it was designed to expose you to
- basic API
- authentication with API key and JWT tokens
- exposure to CORS

❓Compare Amazon ECS on Fargate with AWS Lightsail Containers
- How can Lightsail Containers reduce the cost? How are Lightsail Container costs more predictable?
- What advanced features do you gain on Amazon ECS?

## Learn More
### Reading suggestions
I recommend reading/learning more! Here are some free and some paid resources that you may already have access to
- https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/application.html
- https://www.pluralsight.com/courses/introduction-amazon-elastic-container-service
- https://www.udemy.com/topic/amazon-ecs/?utm_source=
- https://www.f5.com/labs/learning-center/securing-apis-10-best-practices-for-keeping-your-data-and-infrastructure-safe

### Compare AWS Fargate to other Serverless Technologies
- https://duttaaniruddha31.medium.com/aws-fargate-vs-google-cloud-run-f6706e1e6147
- https://blog.iron.io/aws-fargate-vs-azure-containers/
