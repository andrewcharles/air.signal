import ee
from google.oauth2 import service_account
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession

def eeauth(eekey = 'secret-key'):
  """ Initialise earth engine """
  credentials = service_account.Credentials.from_service_account_file(eekey)
  storage_client = storage.Client(credentials=credentials)
  scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
  session = AuthorizedSession(scoped_credentials)
  ee.Initialize(scoped_credentials)

