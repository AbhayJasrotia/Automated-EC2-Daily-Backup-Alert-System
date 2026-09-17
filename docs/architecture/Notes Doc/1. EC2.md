
Today I created the EC2 server that will be used for my automated backup project.

### What I learned

- EC2 is a virtual server in AWS.
    
- An EC2 instance uses EBS for its storage.
    
- The EBS volume is what I will eventually back up.
    
- An EC2 SSH username is different from an AWS IAM username.
    
- I connected to the server using SSH.
    
- I created a test file on the server.
    

### Project structure

```text
EC2
 ↓
EBS Volume
 ↓
EBS Snapshot
 ↓
Lambda automation
 ↓
SNS notification
```

### Today's goal

Get a working EC2 server ready for the backup automation.