#! /bin/bash
#environment location: $ENVPATH
ENV_NAME=airsig2
conda create -y --name $ENV_NAME
source /home/charlesan/miniconda3/bin/activate $ENV_NAME
conda install -y pyyaml
conda install -y -c conda-forge earthengine-api
#pip install earthengine-api --upgrade 
pip install git+https://github.com/andrewcharles/gee_tools.git
#pip install rasterio
pip install geopandas
conda env export --name $ENV_NAME > ${ENV_NAME}-environment.yml

# To create from this file
# conda env create -f ${ENV_NAME}-environment.yml
# conda activate $ENV_NAME 
