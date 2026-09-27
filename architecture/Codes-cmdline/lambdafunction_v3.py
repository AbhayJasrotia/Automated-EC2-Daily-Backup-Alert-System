import boto3
import os
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")
sns = boto3.client("sns")

INSTANCE_ID = os.environ["INSTANCE_ID"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "7"))


def lambda_handler(event, context):

    timestamp = datetime.now(timezone.utc)
    timestamp_text = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

    print("===== EC2 BACKUP STARTED =====")
    print(f"Instance: {INSTANCE_ID}")
    print(f"Time: {timestamp_text}")
    print(f"Retention period: {RETENTION_DAYS} days")

    created_snapshots = []
    deleted_snapshots = []

    try:

        # --------------------------------------------------
        # 1. Find EC2 instance
        # --------------------------------------------------

        response = ec2.describe_instances(
            InstanceIds=[INSTANCE_ID]
        )

        instance = response["Reservations"][0]["Instances"][0]

        # --------------------------------------------------
        # 2. Find attached EBS volumes
        # --------------------------------------------------

        volume_ids = []

        for device in instance["BlockDeviceMappings"]:

            if "Ebs" in device:
                volume_ids.append(
                    device["Ebs"]["VolumeId"]
                )

        print(f"EBS volumes found: {volume_ids}")

        # --------------------------------------------------
        # 3. Create new snapshots
        # --------------------------------------------------

        for volume_id in volume_ids:

            print(f"Creating snapshot for volume: {volume_id}")

            snapshot = ec2.create_snapshot(
                VolumeId=volume_id,
                Description="Automated EC2 backup"
            )

            snapshot_id = snapshot["SnapshotId"]

            # Tag the snapshot
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
                        "Value": "backup-demo-server"
                    },
                    {
                        "Key": "CreatedBy",
                        "Value": "Lambda"
                    }
                ]
            )

            created_snapshots.append(snapshot_id)

            print(f"Snapshot created: {snapshot_id}")

        # --------------------------------------------------
        # 4. Find old backup snapshots
        # --------------------------------------------------

        cutoff_time = timestamp - timedelta(
            days=RETENTION_DAYS
        )

        print(
            f"Deleting project snapshots older than: "
            f"{cutoff_time.isoformat()}"
        )

        snapshots_response = ec2.describe_snapshots(
            OwnerIds=["self"],
            Filters=[
                {
                    "Name": "tag:BackupType",
                    "Values": ["Automated"]
                },
                {
                    "Name": "tag:CreatedBy",
                    "Values": ["Lambda"]
                },
                {
                    "Name": "tag:Source",
                    "Values": ["backup-demo-server"]
                },
                {
                    "Name": "status",
                    "Values": ["completed"]
                }
            ]
        )

        # --------------------------------------------------
        # 5. Delete snapshots older than retention period
        # --------------------------------------------------

        for snapshot in snapshots_response["Snapshots"]:

            snapshot_id = snapshot["SnapshotId"]
            start_time = snapshot["StartTime"]

            if start_time < cutoff_time:

                print(
                    f"Deleting old snapshot: "
                    f"{snapshot_id}"
                )

                ec2.delete_snapshot(
                    SnapshotId=snapshot_id
                )

                deleted_snapshots.append(snapshot_id)

        # --------------------------------------------------
        # 6. Send success notification
        # --------------------------------------------------

        message = (
            "EC2 BACKUP SUCCESSFUL\n\n"
            f"Instance: {INSTANCE_ID}\n"
            f"Time: {timestamp_text}\n"
            f"Retention: {RETENTION_DAYS} days\n\n"
            f"New snapshots:\n"
            f"{', '.join(created_snapshots) if created_snapshots else 'None'}\n\n"
            f"Deleted old snapshots:\n"
            f"{', '.join(deleted_snapshots) if deleted_snapshots else 'None'}"
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
            "created_snapshots": created_snapshots,
            "deleted_snapshots": deleted_snapshots
        }

    except Exception as e:

        print("===== EC2 BACKUP FAILED =====")
        print(f"Error: {str(e)}")

        error_message = (
            "EC2 BACKUP FAILED\n\n"
            f"Instance: {INSTANCE_ID}\n"
            f"Time: {timestamp_text}\n\n"
            f"Error: {str(e)}"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EC2 Backup FAILED",
            Message=error_message
        )

        raise