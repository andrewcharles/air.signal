ENVIRONMENT = "dev"

XMIN = ''
XMAX = ''
YMIN = ''
YMAX = ''

CLAT,CLON = (YMIN+YMAX)/2,(XMIN+XMAX)/2

PROJECT_ID = ""
BUCKET_NAME = ""
OUTPUT_BUCKET = ''

# Define a first set of dates
START_DATE = "2023-02-01"
END_DATE =  "2023-02-09"

COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'
BANDS = ['B2','B3','B4','B8','QA60']
CLOUD_LIMIT = 50
CLOUD_FILTER = 60
CLD_PRB_THRESH = 50
NIR_DRK_THRESH = 0.15
CLD_PRJ_DIST = 1
BUFFER = 50
START_DATE = "2023-01-01"
END_DATE =  "2023-02-01"

REGION = "us-central1"
USER_NAME = ''

AS_SERVICE_ACCOUNT=''
AS_KEY=''
AS_EE_KEY=''
AS_KEYFILE=''