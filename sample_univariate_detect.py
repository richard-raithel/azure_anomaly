from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.ai.anomalydetector.models import *
from azure.core.credentials import AzureKeyCredential
import pandas as pd
import plotly.graph_objects as go
import os

API_KEY = os.environ['ANOMALY_DETECTOR_API_KEY']
ENDPOINT = os.environ['ANOMALY_DETECTOR_ENDPOINT']
DATA_PATH = "univariate_data.csv"

client = AnomalyDetectorClient(ENDPOINT, AzureKeyCredential(API_KEY))

series = []
data_file = pd.read_csv(DATA_PATH, header=None, encoding='utf-8', parse_dates=[0])
for index, row in data_file.iterrows():
    series.append(TimeSeriesPoint(timestamp=row[0].isoformat(), value=row[1]))

request = UnivariateDetectionOptions(series=series, granularity=TimeGranularity.DAILY)

change_point_response = client.detect_univariate_change_point(request)
anomaly_response = client.detect_univariate_entire_series(request)

dates = [point.timestamp for point in series]
values = [point.value for point in series]

# Create a scatter plot using Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=dates, y=values, mode='markers', name='Data'))

for i, (date, value) in enumerate(zip(dates, values)):
    if change_point_response.is_change_point[i]:
        fig.add_trace(go.Scatter(x=[date], y=[value], mode='markers', name='Change Point', marker=dict(color='blue', symbol='square')))
        print("Change point detected at index:", i)
    elif anomaly_response.is_anomaly[i]:
        fig.add_trace(go.Scatter(x=[date], y=[value], mode='markers', name='Anomaly', marker=dict(color='red', symbol='triangle-up')))
        print("Anomaly detected at index:", i)
    else:
        fig.add_trace(go.Scatter(x=[date], y=[value], mode='markers', name='Normal', marker=dict(color='green', symbol='circle')))

fig.show()
