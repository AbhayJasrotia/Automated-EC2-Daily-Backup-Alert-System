# Automated EC2 Daily Backup & Alert System

This is a small AWS project I'm building to automate daily backups of EC2 instances and get notified when they run.

The idea is pretty simple: a scheduled Lambda function takes an EBS snapshot of a given EC2 volume, and once it's done, it sends a notification so I know the backup actually happened (or if it failed).

I started this to get hands-on practice with IAM roles, Lambda, and event-driven automation on AWS, rather than just reading about them.

## What it does

- Runs on a schedule via EventBridge Scheduler
- Creates an EBS snapshot of the target EC2 volume
- Sends an SNS email notification once the backup completes — success or failure
- Logs every run to CloudWatch so I can go back and check what happened

## How it's put together

A Lambda function assumes an IAM role (`EC2BackupLambdaRole`) that's scoped to only the permissions it actually needs — creating snapshots, publishing to SNS, and writing logs to CloudWatch. Nothing more.

```
EventBridge Schedule
        |
        v
      Lambda  --assumes-->  EC2BackupLambdaRole
                                  |
                    +-------------+-------------+
                    |             |             |
               EBS Snapshot   SNS Publish   CloudWatch Logs
```

## Tools used

AWS Lambda, IAM, EBS, SNS, CloudWatch, EventBridge (for the schedule).

## Where it stands right now

The core pipeline is working end to end:

- IAM role and scoped policy are set up and attached to the function
- Lambda creates a snapshot of the target volume and sends an SNS email on success
- Tested the failure path too — pointed it at a bad instance ID on purpose and confirmed it sends a failure notification instead of failing silently
- CloudWatch logs confirm each run (instance, volume, snapshot ID, timing)
- EventBridge Scheduler is wired up and triggering the function automatically — running on a longer interval for now while I keep an eye on it, will switch it to a proper daily rate once I'm confident it's stable

Next up: automatic cleanup of old snapshots (retention), and maybe extending this to back up more than one instance.

## Repo

https://github.com/AbhayJasrotia/Automated-EC2-Daily-Backup-Alert-System