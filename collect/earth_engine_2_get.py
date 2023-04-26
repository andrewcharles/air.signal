# Earth engine to storage bucket
from google.oauth2 import service_account
from google.cloud import storage
import os

PROJECT_ID = "earth-engine-workflow"
BUCKET_NAME = "airsignal2023"
REGION = "us-central1"
USER_NAME = 'charlesan'
OUTPUT_BUCKET = 'airsignal2023'
# Define a first set of dates
START_DATE = "2023-02-01"
END_DATE =  "2023-03-01"

credentials = service_account.Credentials.from_service_account_file(os.getenv('EE_KEY'))
storage_client = storage.Client(credentials=credentials)
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

ROI_POLY = ee.Geometry.Polygon([[[xmin, ymax],
                          [xmin, ymin],
                          [xmax, ymin],
                          [xmax, ymax]]])
lat,lon = (ymin+ymax)/2,(xmin+xmax)/2


# SENTINEL FUNCTIONS
# Use QA for mask then discard
#https://github.com/davemlz/ee-catalog-scale-offset-params/blob/main/list/ee-catalog-scale-offset-parameters.json
BANDS = ['B2','B3','B4','B8','QA60']
CLOUD_LIMIT = 50

def se2mask(image):
    quality_band = image.select('QA60')
    # using the bit mask for clouds and cirrus clouds respectively
    cloudmask = 1 << 10
    cirrusmask = 1 << 11    
    # we only want clear skies
    mask = quality_band.bitwiseAnd(cloudmask).eq(0) and (quality_band.bitwiseAnd(cirrusmask).eq(0)) 
    # we'll divide by 10000 to make interpreting the reflectance values easier
    return image.updateMask(mask)#.divide(10000)

def scale(image):
  bands = ['B2','B3','B4','B8']
  image = image.select(bands).multiply(0.0001)
  #image = image.addBands(im2.select(bands))
  return image

def mosaicByDate(imcol_to_mosaic):
  default_projection_func = imcol_to_mosaic.first().select(imcol_to_mosaic.first().bandNames()).projection()
  imlist = imcol_to_mosaic.toList(imcol_to_mosaic.size())
  unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()

  def match_dates(d):
    d = ee.Date(d)
    dateString = ee.Date(d).format('yyyy-MM-dd')
    im = imcol_to_mosaic.filterDate(d, d.advance(1, "day")).mosaic().setDefaultProjection(default_projection_func)
    return im.set(
        "system:time_start", d.millis(), 
        "system:id", d.format("YYYY-MM-dd")).copyProperties(imcol_to_mosaic)#.rename(dateString)

  mosaic_imlist = unique_dates.map(match_dates)
  return ee.ImageCollection(mosaic_imlist)

def rename_date(img):
  date_string = ee.Image(img).date().format("_YYYY-MM-dd")
  rstr = img.bandNames().map(lambda bandname: ee.String(bandname).cat(date_string))
  img = img.rename(rstr)
  return img

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