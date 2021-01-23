import logging
import os
import sys
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

AWS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
bucket = "kiwi-bot"
prefix = "databases_csv/"

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET,
)


def get_all_objects(bucket, prefix):
    df_list = []

    for obj in s3.list_objects_v2(Bucket=bucket, Prefix=prefix)["Contents"][1:]:
        key = obj["Key"]
        read_file = s3.get_object(Bucket=bucket, Key=key)

        df = pd.read_csv(read_file["Body"])
        df_list.append(df)

    yield from tuple(df_list)


df_kiwer, df_order = get_all_objects(bucket=bucket, prefix=prefix)
print("Files succesfully loaded")
