import logging
import os
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

AWS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
buckets3 = "kiwi-bot"
key = "data/ordersDB.csv"
filepath = "kiwi_bot\data"

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET,
)

# This code extract single object specified manually in the path
# s3.download_file(Bucket=buckets3, Filename=filepath, Key=key)
