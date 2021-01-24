import logging
import os
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

AWS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Information of origin bucket and directory to download files
bucket = "kiwi-bot"
s3_folder = "data/"
filepath = "/data"

s3 = boto3.resource(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET,
)


def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    """
    Download the contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    bucket = s3.Bucket(bucket_name)

    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = (
            obj.key
            if local_dir is None
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        )
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue
        bucket.download_file(obj.key, target)
        print(f"file succesfully downloaded: {target[14:]}")


download_s3_folder(bucket_name=bucket, s3_folder=s3_folder, local_dir=filepath)
