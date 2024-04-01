# Prerequisites
This lab is written for a Windows 11 system. Throughout you will see references to "iploc8.com". You will need to adapt the steps to your own domain name and configuration.

Required knowledge and understanding
- Cloud Computing basics and what AWS is (Free Udemy course [link](https://www.udemy.com/course/introduction-to-aws-cloud-computing/))
- What container computing is
  - https://aws.amazon.com/containers/
- Docker exposure
  - https://docs.docker.com/get-started/
- HTML and PHP exposure
  - https://www.php.net/manual/en/getting-started.php

Required resources
- You will need a [login to the AWS Management Console](https://console.aws.amazon.com)
- You will need to fund your experiments and projects on AWS using a credit card
  - CAUTION It is your responsibility to clean up everything you don't need, because AWS payment terms and conditions apply!
- If you do not already have a domain name in AWS DNS to use, you will want to register one
    - https://aws.amazon.com/route53/pricing/ has a list of pricing by TLD
    - .click $3
    - .link $5
 - Install AWS Cli on your local machine
     - https://aws.amazon.com/cli/
     - Find **Windows** Download and run the 64-bit Windows installer
     - Download and launch AWSCLIV2.msi
     - Accept the terms and defaults
   - Install Docker on your local machine
       - https://docs.docker.com/desktop/install/windows-install/
   - Install Git on your local machine
       - https://learn.microsoft.com/en-us/devops/develop/git/install-and-set-up-git
       - You will need to re-open your command line/shell to use the git commands
# Assumptions
You are responsible for selecting an AWS region where you will build your lab. In my examples, I will use us-east-1 (N. Virginia). I use us-west-2 and eu-central-1 as additional regions.
