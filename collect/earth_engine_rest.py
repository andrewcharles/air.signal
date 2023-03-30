
from google.oauth2 import service_account
#credentials = service_account.Credentials.from_service_account_file('./earth-engine-workflow-013a80bf4f5b.json')
credentials = service_account.Credentials.from_service_account_file('./my-secret-key.json')
#service_account = 'harvester@earth-engine-workflow.iam.gserviceaccount.com'
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
from google.auth.transport.requests import AuthorizedSession
session = AuthorizedSession(scoped_credentials)