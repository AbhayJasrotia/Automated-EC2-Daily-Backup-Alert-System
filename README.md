# Automated EC2 Daily Backup & Alert System

This is a small AWS project I'm building to automate daily backups of EC2 instances and get notified when they run.

The idea is pretty simple: a scheduled Lambda function takes an EBS snapshot of a given EC2 volume every day, and once it's done, it sends a notification so I know the backup actually happened (or if it failed).

I started this to get hands-on practice with IAM roles, Lambda, and event-driven automation on AWS, rather than just reading about them.

## What it does

- Runs on a daily schedule
- Creates an EBS snapshot of the target EC2 volume
- Sends a notification once the backup completes
- Logs everything so I can check what happened later

## How it's put together

A Lambda function assumes an IAM role (`EC2BackupLambdaRole`) that's scoped to only the permissions it actually needs — creating snapshots, publishing to SNS, and writing logs to CloudWatch. Nothing more.

```
Lambda  --assumes-->  EC2BackupLambdaRole
                            |
              +-------------+-------------+
              |             |             |
         EBS Snapshot   SNS Publish   CloudWatch Logs
```

## Tools used

AWS Lambda, IAM, EBS, SNS, CloudWatch, EventBridge (for the schedule).

## Where it stands right now

Just getting started — setting up the IAM role and permissions first, then moving on to the Lambda function itself. I'll update this as it comes together.

## Repo

https://github.com/AbhayJasrotia/Automated-EC2-Daily-Backup-Alert-System