# Script to initialise and check environment is configured.
import os

from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(os.getenv('EE_KEY'))
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
from google.auth.transport.requests import AuthorizedSession
session = AuthorizedSession(scoped_credentials)

import ee 
ee.Initialize(scoped_credentials)

# Anglesea Heath
xmin = 144.3
xmax = 144.25
ymin = -38.3
ymax = -38.44

from google.oauth2 import service_account
from google.cloud import storage

PROJECT_ID = "earth-engine-workflow"
OUTPUT_BUCKET = 'airsignal2023'
REGION = "us-central1"
USER_NAME = 'charlesan'

storage_client = storage.Client(credentials=credentials)

def create_bucket(bucket_name):
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created'.format(bucket.name))

def bucket_exists(bucket_name):
    bucket = storage_client.bucket(bucket_name)
    try:
        bucket.reload()
        return True
    except Exception as e:
        print(e)
        return False

# Replace <BUCKET_NAME> with the name of your bucket
if bucket_exists(OUTPUT_BUCKET):
  print('Bucket exists')
else:
  print('Bucket does not exist')
  create_bucket(OUTPUT_BUCKET)


blobs = storage_client.list_blobs(OUTPUT_BUCKET)
# Note: The call returns a response only when the iterator is consumed.
for blob in blobs:
  print(blob.name)