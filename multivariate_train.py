import os
import time
from datetime import datetime

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *
from dotenv import load_dotenv


# 1. Verify anomaly detector key and endpoint
# 2. Set blob_url
# 3. Set training parameters

load_dotenv()

# Set up anomaly detector credentials
SUBSCRIPTION_KEY = os.environ['ANOMALY_DETECTOR_KEY']
ANOMALY_DETECTOR_ENDPOINT = os.environ['ANOMALY_DETECTOR_ENDPOINT']
ad_client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

# set the time format and blob url
time_format = "%Y-%m-%dT00:00:00Z"
# blob_url = "https://labinsightdataapprigs.blob.core.windows.net/uk-multi-ad-poc/multivariate_data.csv"  # demostration file
blob_url = "https://labinsightdataapprigs.blob.core.windows.net/uk-multi-ad-poc/NissanMotorManufacturing_Nismot_FuchsAnticoritPl3802-39Lv8_1332979.csv"

# set training parameters
train_body = ModelInfo(
    data_source=blob_url,
    # start_time=datetime.strptime("2021-01-01T00:00:00Z", time_format),
    # end_time=datetime.strptime("2021-01-01T06:00:00Z", time_format),
    start_time=datetime.strptime("2022-01-12T00:00:00Z", time_format),
    end_time=datetime.strptime("2022-12-23T00:00:00Z", time_format),
    data_schema="OneTable",
    display_name="sample",
    sliding_window=28,
    align_policy=AlignPolicy(
        align_mode=AlignMode.OUTER,
        fill_n_a_method=FillNAMethod.LINEAR,
        padding_value=0,
    ),
)

# begin training
print("Training new model...")
model = ad_client.train_multivariate_model(train_body)
model_id = model.model_id
print("Training model id is {}".format(model_id))

model_status = None
model = None

# wait until model is ready
while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
    model = ad_client.get_multivariate_model(model_id)
    model_status = model.model_info.status
    print("Model is {}".format(model_status))
    time.sleep(5)
if model_status == ModelStatus.FAILED:
    error = ad_client.get_multivariate_model(model_id).model_info.errors[0].message
    print(error)
if model_status == ModelStatus.READY:
    print("TRAINING COMPLETE")

# Return the latest model id
with open('model_id.txt', 'w') as f:
    f.write(model_id)
