# Automated EC2 Daily Backup & Alert System

This is a small AWS project I built while learning cloud, networking,
IAM, EC2, storage, and automation.

The main idea was simple: **automatically create backups of an EC2
server and get an email when the backup succeeds or fails.**

I also tested the recovery process by creating a new EBS volume from a
snapshot and recovering the test files from it.

## What I used

-   Amazon EC2
-   Amazon EBS
-   EBS Snapshots
-   AWS Lambda
-   Python / Boto3
-   Amazon EventBridge Scheduler
-   Amazon SNS
-   AWS IAM
-   Amazon CloudWatch

## How it works

``` text
EventBridge Scheduler
        |
        v
      Lambda
        |
        v
   EC2 / EBS Volume
        |
        v
   EBS Snapshot
        |
        +--------> SNS --------> Email
        |
        +--------> CloudWatch Logs
```

The Lambda function finds the EBS volumes attached to my EC2 instance
and starts snapshot creation.

EventBridge Scheduler runs the Lambda automatically.

SNS sends an email with the backup status, and CloudWatch stores the
Lambda execution logs.

## Recovery test

I didn't stop at creating a snapshot. I also tested whether the backup
could actually be recovered.

I:

1.  Created an EBS snapshot.
2.  Created a new EBS volume from the snapshot.
3.  Attached the volume to the EC2 instance.
4.  Detected the new disk from Linux using `lsblk`.
5.  Mounted the recovered filesystem.
6.  Found my original test data.
7.  Verified `important-data.txt` and `project-info.txt`.
8.  Unmounted the recovery volume after testing.

This confirmed that the snapshot could be used to recover the test data.

## IAM

The Lambda function uses an IAM execution role instead of storing AWS
access keys in the code.

The role gives Lambda permissions needed for:

-   Creating and describing EC2/EBS resources
-   Creating tags on snapshots
-   Publishing SNS notifications
-   Writing logs to CloudWatch

I also worked on reducing the permissions to what the project actually
needs as part of learning IAM and least privilege.

## Failure testing

I tested the failure path as well.

The Lambda function sends a failure notification through SNS when an
error occurs, and the error is also visible in CloudWatch Logs.

So the project has both:

``` text
Successful backup -> SNS success email
Failed backup     -> SNS failure email
```

## Some Linux commands I used during recovery

``` bash
lsblk
lsblk -f
sudo mkdir /mnt/recovery
sudo mount -o nouuid /dev/nvme1n1p1 /mnt/recovery
mount | grep /mnt/recovery
sudo find /mnt/recovery -name "backup-data" -type d 2>/dev/null
ls -la /mnt/recovery/home/ec2-user/backup-data
sudo umount /mnt/recovery
```

These commands helped me identify the attached disks, mount the
recovered filesystem, verify the backed-up files, and clean up the
recovery mount.

## What I learned

This project helped me understand how several AWS services fit together
instead of learning them separately.

The main things I practiced were:

-   EC2 and EBS
-   EBS snapshots and recovery
-   IAM roles and permissions
-   Lambda automation with Python/Boto3
-   EventBridge scheduling
-   SNS notifications
-   CloudWatch logging
-   Linux disk and filesystem commands
-   Backup failure testing
-   Recovery testing
-   Basic AWS cost awareness and resource cleanup

## Project structure

``` text
aws-ec2-automated-backup/
|
├── README.md
├── lambda/
│   └── backup_lambda.py
├── docs/
│   ├── architecture/
│   │   └── architecture.png
│   └── screenshots/
└── notes/
    ├── day-01.md
    ├── day-02.md
    ├── day-03.md
    ├── day-04.md
    ├── day-05.md
    ├── day-06.md
    ├── day-07.md
    ├── day-08.md
    ├── day-09.md
    └── day-10.md
```

## Security

I did not put AWS access keys, secret keys, passwords, or my `.pem` file
in this repository.

For public screenshots, sensitive resource details such as account
information, email addresses, public IPs, and other identifiers should
also be hidden where appropriate.

## Final result

The final workflow is:

``` text
EC2
 |
 | EBS
 v
Lambda
 |
 +--> EBS Snapshot
 |
 +--> SNS Email
 |
 +--> CloudWatch Logs

EventBridge Scheduler
 |
 +--> triggers Lambda daily
```

The project started as a way to learn AWS by building something
practical, and the main goal was to understand **how the services
connect and how a real backup workflow can be automated and tested.**
