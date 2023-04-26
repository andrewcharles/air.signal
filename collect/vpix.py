# read tifs
import rasterio as rs
from rasterio.plot import show
fp = r'../data/reedy_lake_rgbnir.tif'
with rs.open(fp) as dataset:
    dataset.count, dataset.height, dataset.width
    # Coordinate Reference System
    dataset.crs
    #print(dataset.dataset_mask())
    #band1 = dataset.read(1)

fp = r'../data/sig.mon/frac_1.tif'
import xarray as xr
xds = xr.open_dataset(fp)

['pv', 'npv', 'bare', 'crypto', 'pg', 'pnpv', 'b2', 'b3', 'b4', 'b5',
       'b7', 'ndvi', 'burn', 'ndwi'],
