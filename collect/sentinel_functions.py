# SENTINEL FUNCTIONS
# Use QA for mask then discard
#https://github.com/davemlz/ee-catalog-scale-offset-params/blob/main/list/ee-catalog-scale-offset-parameters.json
BANDS = ['B2','B3','B4','B8','QA60']
CLOUD_LIMIT = 50
# 8A is for masking the edges
ALL_BANDS = ['B4','B8','B8A','B9','QA60']
BANDS = ALL_BANDS
CLOUD_LIMIT = 75
CLOUD_FILTER = CLOUD_LIMIT
MAX_CLOUD_PROBABILITY = 95
CLD_PRB_THRESH = MAX_CLOUD_PROBABILITY
NIR_DRK_THRESH = 0.15
CLD_PRJ_DIST = 1
BUFFER = 50
COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'

import ee 
from urllib.request import urlopen
import json
import os
url = "https://raw.githubusercontent.com/davemlz/ee-catalog-scale-offset-params/main/list/ee-catalog-scale-offset-parameters.json"
scaling_factor_filename = 'ee-catalog-scale-offset-parameters.json'

if os.path.isfile(scaling_factor_filename):
  print("reading scale from file")
  with open(scaling_factor_filename, 'r') as f:
    scaling_factors = json.loads(f.read())
else:
  print("download scale")
  response = urlopen(url)
  scaling_factors = json.loads(response.read())
  with open(scaling_factor_filename, 'w') as f:
      json.dump(scaling_factors, f)

def se2mask(image):
  quality_band = image.select('QA60')
  cloudmask = 1 << 10
  cirrusmask = 1 << 11
  mask = quality_band.bitwiseAnd(cloudmask).eq(0) and (quality_band.bitwiseAnd(cirrusmask).eq(0))
  return image.updateMask(mask)

# make a list of scaled bands and replace all at once
def scale(image, bands=BANDS, collection=COLLECTION):
  scaled_bands = []
  for band_name in bands:
    img_band = image.select(band_name).multiply(
      scaling_factors[collection][band_name]['scale']).add(scaling_factors[collection][band_name]['offset'])
    scaled_bands.append(img_band)  
  image = image.addBands(scaled_bands, bands, True)
  return image

def easy_scale(image, bands=BANDS):
  for band_name in bands:
    img_band = image.select(band_name).multiply(0.001)
    image = image.addBands(img_band, [band_name], True)
  return image

# The masks for the 10m bands sometimes do not exclude bad data at
# scene edges, so we apply masks from the 20m and 60m bands as well.
def maskEdges(s2_img):
  return s2_img.updateMask(
      s2_img.select('B8A').mask().updateMask(
          s2_img.select('B9').mask()))

def se2SCLmask(image):
  # mask sentinel 2 using the SCL band
  # these categories mean:
  # keep these values
  qa1 = image.select('SCL').neq(4)
  qa2 = image.select('SCL').neq(5)
  qa3 = image.select('SCL').neq(7)
  qa = qa1.And(qa2).And(qa3)
  #qa = qa1
  # Masked classes set to zero
  mask = qa.eq(0)
  return(image.updateMask(mask))

def addNDVI(image):
  ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
  return image.addBands(ndvi)

# Cloud masking function
def maskClouds(img,MAX_CLOUD_PROBABILITY=MAX_CLOUD_PROBABILITY):
  clouds = ee.Image(img.get('cloud_mask')).select('probability')
  isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY)
  return img.updateMask(isNotCloud)

def add_cloud_bands(img):
    # Get s2cloudless image, subset the probability band.
    cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

    # Condition s2cloudless by the probability threshold value.
    is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')

    # Add the cloud probability layer and cloud mask as image bands.
    return img.addBands(ee.Image([cld_prb, is_cloud]))

"""Define a function to add dark pixels, cloud projection, and 
identified shadows as bands to an S2 SR image input. Note that 
the image input needs to be the result of the above add_cloud_bands 
function because it relies on knowing which pixels are 
considered cloudy ('clouds' band).
"""
def add_shadow_bands(img):
    # Identify water pixels from the SCL band.
    not_water = img.select('SCL').neq(6)

    # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
    SR_BAND_SCALE = 1e4
    dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')

    # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
    shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

    # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
    cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
        .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
        .select('distance')
        .mask()
        .rename('cloud_transform'))

    # Identify the intersection of dark pixels with cloud shadow projection.
    shadows = cld_proj.multiply(dark_pixels).rename('shadows')

    # Add dark pixels, cloud projection, and identified shadows as image bands.
    return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))

def add_cld_shdw_mask(img):
    # Add cloud component bands.
    img_cloud = add_cloud_bands(img)

    # Add cloud shadow component bands.
    img_cloud_shadow = add_shadow_bands(img_cloud)

    # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
    is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

    # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
    # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
    is_cld_shdw = (is_cld_shdw.focalMin(2).focalMax(BUFFER*2/20)
        .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
        .rename('cloudmask'))

    # Add the final cloud-shadow mask to the image.
    return img_cloud_shadow.addBands(is_cld_shdw)

# add the date to band names to help with the stack
def rename_date(img):
  date_string = ee.Image(img).date().format("_YYYY-MM-dd")
  rstr = img.bandNames().map(lambda bandname: ee.String(bandname).cat(date_string))
  img = img.rename(rstr)
  return img

"""Define a function to filter the SR and s2cloudless collections 
according to area of interest and date parameters, then join them on the 
system:index property. The result is a copy of the SR collection where each 
image has a new 's2cloudless' property whose value is the corresponding 
s2cloudless image."""
def get_s2_sr_cld_col(aoi, start_date, end_date):
    # Import and filter S2 SR.
    s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(maskEdges)
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER)))

    # Import and filter s2cloudless.
    s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date))

    # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
    return ee.ImageCollection(ee.Join.saveFirst('cloud_mask').apply(**{
        'primary': s2_sr_col,
        'secondary': s2_cloudless_col,
        'condition': ee.Filter.equals(**{
            'leftField': 'system:index',
            'rightField': 'system:index'
        })
    }))

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

def print_info(imcol):
  imlist = imcol.toList(imcol.size())
  unique_ids = imlist.map(lambda im: ee.Image(im).id()  )
  unique_dates = imlist.map(lambda im: ee.Image(im).date().format("YYYY-MM-dd")).distinct()
  bandnames = imlist.map(lambda im: ee.Image(im).bandNames()  )
  idslist = ee.List.getInfo(unique_ids)
  print("Image IDs")
  print(idslist)
  print(ee.List.getInfo(unique_dates))
  print(ee.List.getInfo(bandnames))

if __name__ == "__main__":
  print("Running")