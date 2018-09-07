import boto3
from datetime import datetime
import json
import logging
import os
import sys
import traceback

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

for noisy in ('botocore', 'boto3', 'requests'):
    logging.getLogger(noisy).level = logging.WARN

DDB = boto3.resource("dynamodb").Table(os.environ["DATA_TABLE"])

def make_response(body, code=200, headers={}, base64=False):
    _headers = {"Content-Type": "text/html"}
    _headers.update(headers)
    return {
        "body": body,
        "statusCode": code,
        "headers": _headers,
        "isBase64Encoded": base64
    }

def apigateway_handler(event, context):
    print(json.dumps(event))
    if event["path"] == "/store" and event["httpMethod"] == "GET":
        params = event.get("queryStringParameters")
        params = params if params else {}
        if params.get("source") and params.get("value"):
            item = {
                "source":params.get("source"),
                "value":str(params.get("value")),
                "timestamp":now()
            }
            response = DDB.put_item(Item=item)
            logging.debug(response)
            return make_response(body="{}", code=200, headers={"Content-Type": "text/json"})
        else:
            logging.warn("Missing either/both of value and source.")
    else:
        logging.warn("Method or path are incorrect.")
    return make_response(body="Required arguments are missing.", code=400)

def now():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S%z")
