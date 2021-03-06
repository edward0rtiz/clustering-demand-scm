import logging
import os
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError

AWS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")
bucket = "kiwi-bot"
# key = "ordersDB.csv"
prefix = "data/"
filename = "https://kiwi-bot.s3.us-east-2.amazonaws.com/ordersDB.csv"
filepath = "kiwi_bot\data\order.csv"

s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET,
)

read_file = s3.get_object(Bucket=bucket, Key=key)

df = pd.read_csv(read_file["Body"])
df.to_csv("kiwi_bot\data\order2.csv")
print("File succesfully loaded")
