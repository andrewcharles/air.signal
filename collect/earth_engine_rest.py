from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(os.getenv('EE_KEY'))
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
from google.auth.transport.requests import AuthorizedSession
session = AuthorizedSession(scoped_credentials)