conda create --name airsig
environment location: $AIRSIGENVPATH
conda env create -f environment.yml
conda env export > environment.yml

mkdir data
conda activate airsig

pip install gradio
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install google-cloud-storage
pip install google-auth
pip install rasterio

# Ipython magic settings
%load_ext autoreload
%autoreload 2

gcloud iam service-accounts keys create $KEY --iam-account $SERVICE_ACCOUNT