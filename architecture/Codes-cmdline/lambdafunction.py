import boto3
import os
from datetime import datetime

ec2 = boto3.client("ec2")
sns = boto3.client("sns")

INSTANCE_ID = os.environ["INSTANCE_ID"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    try:
        # Find the EBS volumes attached to our EC2 instance
        response = ec2.describe_instances(
            InstanceIds=[INSTANCE_ID]
        )

        instance = response["Reservations"][0]["Instances"][0]

        volume_ids = []

        for device in instance["BlockDeviceMappings"]:
            if "Ebs" in device:
                volume_ids.append(device["Ebs"]["VolumeId"])

        # Create a snapshot for each attached EBS volume
        snapshots = []

        for volume_id in volume_ids:

            snapshot = ec2.create_snapshot(
                VolumeId=volume_id,
                Description="Automated EC2 backup"
            )

            snapshots.append(snapshot["SnapshotId"])

        # Send success notification
        message = (
            "EC2 backup completed successfully.\n\n"
            f"Instance: {INSTANCE_ID}\n"
            f"Snapshots: {', '.join(snapshots)}\n"
            f"Time: {datetime.utcnow().isoformat()} UTC"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Backup Successful",
            Message=message
        )

        return {
            "statusCode": 200,
            "snapshots": snapshots
        }

    except Exception as e:

        error_message = (
            "EC2 backup FAILED.\n\n"
            f"Instance: {INSTANCE_ID}\n"
            f"Error: {str(e)}"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Backup FAILED",
            Message=error_message
        )

        raise