# Download from storage bucket to local

from google.oauth2 import service_account
from google.cloud import storage
import logging
import os
from google.cloud import storage
logging.basicConfig(level=logging.DEBUG) 

credentials = service_account.Credentials.from_service_account_file(os.getenv('EE_KEY'))

storage_client = storage.Client(credentials=credentials)
OUTPUT_BUCKET = 'airsignal2023'
folder = "../data/sig.mon"

blobs = storage_client.list_blobs(OUTPUT_BUCKET)

for blob in blobs:
    logging.info("Blobs: {}".format(blob.name))
    destination_uri = "{}/{}".format(folder, blob.name) 
    if(not os.path.isfile(destination_uri)):
        blob.download_to_filename(destination_uri)
    else:
        print("has")


