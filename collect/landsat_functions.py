import geopandas as gpd
import numpy as np
import ee 

BANDS = ['B2','B3','B4','B8','QA60']

# See landsat documentation: https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1619_Landsat8-9-Collection2-Level2-Science-Product-Guide-v5.pdf
BITS_LANDSAT_PIXEL_QA_L8 = {
    '0': {0:'image', 1:'fill'},
    '1': {1:'cloud_dilation'},
    '2': {1:'cirrus'},
    '3': {1:'cloud'},
    '4': {1:'shadow'},
    '5': {1:'snow'},
    '6': {1:'clear'},
    '7': {1:'water'},
    '8-9':{3:'high_confidence_cloud'},
    '10-11':{3:'high_confidence_shadow'},
    '12-13': {3:'high_confidence_snow'},
    '14-15': {3:'high_confidence_cirrus'}
}

# aerosol
#Bit Flag Description Values
#0 Fill 0 Pixel is not fill
#1 Pixel is fill
#1 Valid aerosol retrieval 0 Pixel retrieval is not valid
#1 Pixel retrieval is valid
#2 Water 0 Pixel is not water
#1 Pixel is water
#3 Unused 0
#4 Unused 0
#5 Interpolated Aerosol 0 Pixel is not aerosol interpolated
#1 Pixel is aerosol interpolated
#6 Aerosol Level 00 Climatology
#01 Low
#10 Medium
#11 High
# Landsat NDVI functions
def addnd(image,b1,b2,name):
  nd = image.normalizedDifference([b1, b2]).rename(name)
  return image.addBands(nd)

def addNDVI_landsat457(image):
  ndvi = image.normalizedDifference(['B4', 'B3']).rename('NDVI')
  return image.addBands(ndvi)

def addNDVI_landsat89(image):
  ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
  return image.addBands(ndvi)

def addNDVI_L8SR(image):
  ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
  return image.addBands(ndvi)

def addNDWI_landsat457(image):
  ndvi = image.normalizedDifference(['B4', 'B3']).rename('NDWI')
  return image.addBands(ndvi)

def addNDWI_landsat89(image):
  ndvi = image.normalizedDifference(['B3', 'B5']).rename('NDWI')
  return image.addBands(ndvi)

def addNDWI_L8SR(image):
  ndvi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
  return image.addBands(ndvi)

#Landsat 4-5 TM NDWI = (B03 - B05) / (B03 + B05)
#Landsat 7 ETM+ NDWI = (B02 - B04) / (B02 + B04)
#Landsat 8 NDWI = (B03 - B05) / (B03 + B05)
#Landsat 8 NDVI = (B05 - B04) / (B05 + B04)
#Landsat 5 and 7 NDVI = (B04 - B03) / (B04 + B03)

# Define the SR masking function
def maskL457srcloud(image):
    # 4 and 7 both have SR_CLOUD_QA mask
    # Bit 0 - Fill
    # Bit 1 - cloud
    # Bit 2 - cloud shadow
    # Bit 3 - adjacent
    # Bit 4 - snow
    # Bit 4 - 
    cloudShadowBitMask = ee.Number(2).pow(2).int()
    cloudsBitMask = ee.Number(2).pow(1).int()
    qa = image.select('SR_CLOUD_QA')
    qaMask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
      qa.bitwiseAnd(cloudsBitMask).eq(0))

    saturationMask = image.select('QA_RADSAT').eq(0)

    # Apply the scaling factors to the appropriate bands.
    opticalBands = image.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
        .multiply(0.0000275).add(-0.2)
    thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0)

    # Replace the original bands with the scaled ones and apply the masks.
    return image.addBands(opticalBands, None, True) \
        .addBands(thermalBand, None, True) \
        .updateMask(qaMask) \
        .updateMask(saturationMask)

# Define the SR masking function
def maskL457sr(image):
    cloudShadowBitMask = ee.Number(2).pow(4).int()
    cloudsBitMask = ee.Number(2).pow(3).int()
    qa = image.select('QA_PIXEL')
    qaMask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
      qa.bitwiseAnd(cloudsBitMask).eq(0))

    saturationMask = image.select('QA_RADSAT').eq(0)
    # Apply the scaling factors to the appropriate bands.
    opticalBands = image.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
        .multiply(0.0000275).add(-0.2)
    thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0)

    # Replace the original bands with the scaled ones and apply the masks.
    return image.addBands(opticalBands, None, True) \
        .addBands(thermalBand, None, True) \
        .updateMask(qaMask) \
        .updateMask(saturationMask)

# Manually composite TOA  corrections
def maskL457toa(image):
    # Bit 0 - Fill
    # Bit 1 - Dilated Cloud
    # Bit 2 - Unused
    # Bit 3 - Cloud
    # Bit 4 - Cloud Shadow
    cloudShadowBitMask = ee.Number(2).pow(4).int()
    cloudsBitMask = ee.Number(2).pow(3).int()
    qa = image.select('QA_PIXEL')
    qaMask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
      qa.bitwiseAnd(cloudsBitMask).eq(0))
    saturationMask = image.select('QA_RADSAT').eq(0)

    # Apply the scaling factors to the appropriate bands.
    #opticalBands = image.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
    #    .multiply(0.0000275).add(-0.2)
    #thermalBand = image.select('ST_B6').multiply(0.00341802).add(149.0)

    # Replace the original bands with the scaled ones and apply the masks.
    return image.updateMask(qaMask) \
        .updateMask(saturationMask)

def maskL8sr(image):
    # Bit 0 - Fill
    # Bit 1 - Dilated Cloud
    # Bit 2 - Cirrus
    # Bit 3 - Cloud
    # Bit 4 - Cloud Shadow
    # Bit 7 - Water
    # https://gis.stackexchange.com/questions/274048/apply-cloud-mask-to-landsat-imagery-in-google-earth-engine-python-api
    # https://gis.stackexchange.com/questions/363929/how-to-apply-a-bitmask-for-radiometric-saturation-qa-in-a-image-collection-eart
    cloudShadowBitMask = ee.Number(2).pow(4).int()
    cloudsBitMask = ee.Number(2).pow(3).int()
    qa = image.select('QA_PIXEL')
    qaMask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
      qa.bitwiseAnd(cloudsBitMask).eq(0))

    saturationMask = image.select('QA_RADSAT').eq(0)

    # Replace the original bands with the scaled ones and apply the masks.
    return image\
        .updateMask(qaMask) \
        .updateMask(saturationMask)

def scaleL8sr(image):
    # Apply the scaling factors to the appropriate bands.
    opticalBands = image.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7']) \
        .multiply(0.0000275).add(-0.2)
    thermalBand = image.select('ST_B10').multiply(0.00341802).add(149.0)

    # Replace the original bands with the scaled ones and apply the masks.
    return image.addBands(opticalBands, None, True) \
        .addBands(thermalBand, None, True)

def addNDVIandTime(img):
  date = img.date()
  mons = date.difference(ee.Date('1970-01-01'),'month')
  ndvi = img.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
  img = img.addBands(ndvi).addBands(ee.Image(mons).rename('t'))#.addBands(ee.Image.constant(1))
  return ee.Image(img)

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

from urllib.request import urlopen
import json
url = "https://raw.githubusercontent.com/davemlz/ee-catalog-scale-offset-params/main/list/ee-catalog-scale-offset-parameters.json"
response = urlopen(url)
scaling_factors = json.loads(response.read())

# make a list of scaled bands and replace all at once
def scale(image, bands=BANDS):
  scaled_bands = []
  for band_name in bands:
    img_band = image.select(band_name).multiply(scaling_factors[COLLECTION][band_name]['scale']).add(scaling_factors[COLLECTION][band_name]['offset'])
    scaled_bands.append(img_band)
  image = image.addBands(scaled_bands, bands, True)
  return image

#from geetools.cloud_mask import compute
