ROI_POLY = default_region

# @title
import matplotlib.pyplot as plt
def plotgreenL8SR(imcol,idx):
  imlist = imcol.toList(imcol.size())
  img = ee.Image(imlist.get(idx))
  band = 'SR_B2'
  arr = np.array(img.sampleRectangle(region=ROI_POLY,defaultValue=0).get(band).getInfo())
  plt.imshow(arr)

def plotimg(imcol,idx,band='NDVI'):
  imlist = imcol.toList(imcol.size())
  img = ee.Image(imlist.get(idx))
  arr = np.array(img.select(band).sampleRectangle(region=ROI_POLY,defaultValue=0).get(band).getInfo())
  plt.imshow(arr)

def plotrgbL8SR(imcol,idx,scale=1.0,vmin=0,vmax=1):
  imlist = imcol.toList(imcol.size())
  img = ee.Image(imlist.get(idx))
  bands = ['SR_B2','SR_B3','SR_B4']
  red = np.array(img.select(bands).sampleRectangle(region=ROI_POLY,defaultValue=0).get('SR_B4').getInfo())
  gre = np.array(img.select(bands).sampleRectangle(region=ROI_POLY,defaultValue=0).get('SR_B3').getInfo())
  blu = np.array(img.select(bands).sampleRectangle(region=ROI_POLY,defaultValue=0).get('SR_B2').getInfo())
  arr = np.stack([red,gre,blu],axis=2) * scale
  plt.imshow(arr,vmin=vmin,vmax=vmax)



