# !/usr/bin/env python
# coding=utf-8
import ee
from geetools.cloud_mask import compute

def landsatSR(options=('cloud', 'shadow', 'adjacent', 'snow'), name='sr_mask',
              addBands=False, updateMask=True):
    """ Function to use in Landsat Surface Reflectance Collections:
    LANDSAT/LT04/C01/T1_SR, LANDSAT/LT05/C01/T1_SR, LANDSAT/LE07/C01/T1_SR,
    LANDSAT/LC08/C01/T1_SR

    :param options: masks to apply. Options: 'cloud', 'shadow', 'adjacent',
        'snow'
    :type options: list
    :param name: name of the band that will hold the final mask. Default: 'toa_mask'
    :type name: str
    :param addBands: add all bands to the image. Default: False
    :type addBands: bool
    :param updateMask: update the mask of the Image. Default: True
    :type updateMask: bool
    :return: a function for applying the mask
    :rtype: function
    """
    sr = {'bits': ee.Dictionary({'cloud': 1, 'shadow': 2, 'adjacent': 3, 'snow': 4}),
          'band': 'sr_cloud_qa'}

    pix = {'bits': ee.Dictionary({'cloud': 5, 'shadow': 3, 'snow': 4}),
           'band': 'pixel_qa'}

    # Parameters
    options = ee.List(options)

    def wrap(image):
        bands = image.bandNames()
        contains_sr = bands.contains('sr_cloud_qa')
        good_pix = ee.Image(ee.Algorithms.If(contains_sr,
                   compute(image, sr['band'], sr['bits'], options, name_all=name),
                   compute(image, pix['band'], pix['bits'], options, name_all=name)))

        mask = good_pix.select([name]).Not()

        if addBands and updateMask:
            return image.updateMask(mask).addBands(good_pix)
        elif addBands:
            return image.addBands(good_pix)
        elif updateMask:
            return image.updateMask(mask)
        else:
            return image

    return wrap

           #'band': 'QA_PIXEL'}

