import boto3
import os
from datetime import datetime, timezone

ec2 = boto3.client("ec2")
sns = boto3.client("sns")

INSTANCE_ID = os.environ["INSTANCE_ID"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("===== EC2 BACKUP STARTED =====")
    print(f"Instance: {INSTANCE_ID}")
    print(f"Time: {timestamp}")

    try:
        # Find the EC2 instance
        response = ec2.describe_instances(
            InstanceIds=[INSTANCE_ID]
        )

        instance = response["Reservations"][0]["Instances"][0]

        instance_name = "backup-demo-server"

        # Find attached EBS volumes
        volume_ids = []

        for device in instance["BlockDeviceMappings"]:
            if "Ebs" in device:
                volume_ids.append(device["Ebs"]["VolumeId"])

        print(f"EBS volumes found: {volume_ids}")

        snapshots = []

        # Create snapshot for every attached EBS volume
        for volume_id in volume_ids:

            print(f"Creating snapshot for volume: {volume_id}")

            snapshot = ec2.create_snapshot(
                VolumeId=volume_id,
                Description=f"Automated backup of {instance_name}"
            )

            snapshot_id = snapshot["SnapshotId"]

            # Add useful tags
            ec2.create_tags(
                Resources=[snapshot_id],
                Tags=[
                    {
                        "Key": "Name",
                        "Value": "EC2-Daily-Backup"
                    },
                    {
                        "Key": "BackupType",
                        "Value": "Automated"
                    },
                    {
                        "Key": "Source",
                        "Value": instance_name
                    },
                    {
                        "Key": "CreatedBy",
                        "Value": "Lambda"
                    }
                ]
            )

            snapshots.append(snapshot_id)

            print(f"Snapshot created: {snapshot_id}")

        # Success notification
        message = (
            "EC2 BACKUP SUCCESSFUL\n\n"
            f"Instance: {instance_name}\n"
            f"Instance ID: {INSTANCE_ID}\n"
            f"Snapshots: {', '.join(snapshots)}\n"
            f"Time: {timestamp}"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Backup Successful",
            Message=message
        )

        print("Backup notification sent.")
        print("===== EC2 BACKUP COMPLETED =====")

        return {
            "statusCode": 200,
            "snapshots": snapshots
        }

    except Exception as e:

        print("===== EC2 BACKUP FAILED =====")
        print(f"Error: {str(e)}")

        error_message = (
            "EC2 BACKUP FAILED\n\n"
            f"Instance: {INSTANCE_ID}\n"
            f"Time: {timestamp}\n\n"
            f"Error: {str(e)}"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Backup FAILED",
            Message=error_message
        )

        raise