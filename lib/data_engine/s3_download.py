import pandas as pd
import os
import boto3
import logging
from botocore.exceptions import ClientError
from io import StringIO


AWS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.environ.get('AWS_SECRET_ACCESS_KEY')
bucket = "kiwi-bot"
key = "ordersDB.csv"
filename = "https://kiwi-bot.s3.us-east-2.amazonaws.com/ordersDB.csv"
filepath = 'kiwi_bot\data\order.csv'

s3 = boto3.client("s3",
                  region_name="us-east-1",
                  aws_access_key_id=AWS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET)

s3.download_file(Bucket=bucket,
                 Filename=filepath,
                 Key=key)
