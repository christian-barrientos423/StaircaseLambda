import boto3
import json
import csv
import time
from datetime import datetime

S3_CLIENT = boto3.client('s3')
GLUE_CLIENT = boto3.client('glue')
BUCKET_NAME = 'staircase'
FILE_NAME = 'endpoint_stats/invocations.csv'
CRAWLER_NAME = 'staircase-crawler'

def lambda_handler(event, context):
    #Check if file exists on S3
    files_in_bucket = S3_CLIENT.list_objects(Bucket=BUCKET_NAME)
    invocations_file_exists = False
    if "Contents" in files_in_bucket:
        for file in files_in_bucket['Contents']:
            if file['Key'] == FILE_NAME:
                invocations_file_exists = True
            
    #If invocations file exists in bucket, append the current invocation to existing ones
    if invocations_file_exists:
        existing_invocations = S3_CLIENT.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
        lines = existing_invocations['Body'].read().decode('utf-8').splitlines(True)
        reader = csv.reader(lines)
        with open('/tmp/invocations.csv', 'w', newline='') as f:
            w = csv.writer(f, delimiter=',')
            total_calls = 0
            for row in reader:
                w.writerow(row)
                total_calls = total_calls + 1
            w.writerow([time.time(), 'helloworld', total_calls+1])
        with open('/tmp/invocations.csv', 'rb') as data:
            S3_CLIENT.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body=data)
    #If invocations file does not exist, add the current invocation
    else:
        with open('/tmp/invocations.csv', 'w', newline='') as f:
            w = csv.writer(f, delimiter=',')
            w.writerow([time.time(), 'helloworld', 1])
        with open('/tmp/invocations.csv', 'rb') as data:
            S3_CLIENT.put_object(Bucket=BUCKET_NAME, Key=FILE_NAME, Body=data)
    try:
        GLUE_CLIENT.start_crawler(Name=CRAWLER_NAME)
    except GLUE_CLIENT.exceptions.CrawlerRunningException:
        print('Crawler already running')
    return {
        'statusCode': 200,
        'body': json.dumps('ByeWorld')
    }
