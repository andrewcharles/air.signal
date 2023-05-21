# Earth engine to storage bucket
from google.oauth2 import service_account
from google.cloud import storage
import os

# enable local import - hack (TODO: move config to yaml)
import pathlib
import sys
from config import *
EE_KEY = AS_EE_KEY #os.getenv('EE_KEY')

credentials = service_account.Credentials.from_service_account_file(EE_KEY)
storage_client = storage.Client(credentials=credentials)
scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloud-platform'])
from google.auth.transport.requests import AuthorizedSession
session = AuthorizedSession(scoped_credentials)

import ee 
ee.Initialize(scoped_credentials)

ROI_POLY = ee.Geometry.Polygon([[[xmin, ymax],
                          [xmin, ymin],
                          [xmax, ymin],
                          [xmax, ymax]]])
lat,lon = (ymin+ymax)/2,(xmin+xmax)/2

from sentinel_functions import se2mask, scale, mosaicByDate, rename_date
from storage_bucket import create_bucket, bucket_exists

# Replace <BUCKET_NAME> with the name of your bucket
if bucket_exists(OUTPUT_BUCKET, storage_client):
  print('Bucket exists')
else:
  print('Bucket does not exist')
  create_bucket(OUTPUT_BUCKET, storage_client)

blobs = storage_client.list_blobs(OUTPUT_BUCKET)
# Note: The call returns a response only when the iterator is consumed.
for blob in blobs:
  print(blob.name)

imcol = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(ROI_POLY).filterDate(
    START_DATE, END_DATE).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE",CLOUD_LIMIT)).select(BANDS).map(se2mask)

img = imcol.first()
projection = img.select('B2').projection().getInfo();

imcol = mosaicByDate(imcol)#.map(scale)
imcol = imcol.map(rename_date)
imcol = imcol.toBands()
print(ee.List.getInfo(imcol.bandNames()))

# Save 10m bands
task = ee.batch.Export.image.toCloudStorage(**{
  'image': imcol,
  'description': 'image_export_job',
  'crs': 'EPSG:7854',
  'bucket': OUTPUT_BUCKET,
  'fileNamePrefix': 'angle_brick_1',
  #'dimensions':,
  'crs': projection['crs'],
  'scale':10,
  'crsTransform': projection['transform'],
  'region': ROI_POLY,
  'fileFormat': 'GeoTIFF',
  'formatOptions': {
    'cloudOptimized': True
  },
  'maxPixels': 1e8})
task.start()

blobs = client.list_blobs(OUTPUT_BUCKET)
# Note: The call returns a response only when the iterator is consumed.
for blob in blobs:
  print(blob.name)