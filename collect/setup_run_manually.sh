conda create --name airsig
environment location: $AIRSIGENVPATH
conda env create -f environment.yml
conda env export > environment.yml

# to get a snapshot of the current airsig environment

conda activate airsig
conda env export > environment.yml

mkdir data
conda activate airsig

conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
#conda install python=3 geopandas # FAILS
# not conda install geopandas
pip install geopandas
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install google-cloud-storage
pip install google-auth
pip install rasterio
!pip install git+https://github.com/andrewcharles/gee_tools.git

# Ipython magic settings
%load_ext autoreload
%autoreload 2

gcloud iam service-accounts keys create $KEY --iam-account $SERVICE_ACCOUNT