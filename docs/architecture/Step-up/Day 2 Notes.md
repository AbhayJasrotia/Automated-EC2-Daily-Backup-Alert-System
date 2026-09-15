# Day 2 — EBS

Today I learned how EC2 and EBS work together.

## What I learned

- EC2 is the virtual server.
- EBS provides persistent block storage for EC2.
- The files on my EC2 server are stored on its EBS volume.
- An EBS snapshot is used as a point-in-time backup of a volume.
- I checked the EBS volume attached to my EC2 instance.
- I created test data that will be used to verify the backup later.

## Commands I practiced

```bash
mkdir backup-data

echo "This file is part of my AWS automated backup project." > backup-data/project-info.txt

echo "This data should exist after restoring an EBS snapshot." > backup-data/important-data.txt

ls -la backup-data

df -h

lsblk