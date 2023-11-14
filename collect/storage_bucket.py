
def create_bucket(bucket_name, storage_client):
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created'.format(bucket.name))

def bucket_exists(bucket_name, storage_client):
    bucket = storage_client.bucket(bucket_name)
    try:
        bucket.reload()
        return True
    except Exception as e:
        print(e)
        return False
    
from google.oauth2 import service_account
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession

def storage_auth(key):
    credentials = service_account.Credentials.from_service_account_file(key)
    storage_client = storage.Client(credentials=credentials)
    return(storage_client)