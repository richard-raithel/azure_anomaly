import json
import os
import time
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import get_blob_data

from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv


load_dotenv()

# Set up anomaly detector credentials
SUBSCRIPTION_KEY = os.environ['ANOMALY_DETECTOR_KEY']
ANOMALY_DETECTOR_ENDPOINT = os.environ['ANOMALY_DETECTOR_ENDPOINT']
ad_client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

# set the time format and blob url
time_format = "%Y-%m-%dT%H:%M:%SZ"
blob_url = "https://labinsightdataapprigs.blob.core.windows.net/uk-multi-ad-poc/multivariate_data.csv"

# set training parameters
train_body = ModelInfo(
    data_source=blob_url,
    start_time=datetime.strptime("2021-01-01T00:00:00Z", time_format),
    end_time=datetime.strptime("2021-01-01T06:00:00Z", time_format),
    data_schema="OneTable",
    display_name="sample",
    sliding_window=200,
    align_policy=AlignPolicy(
        align_mode=AlignMode.OUTER,
        fill_n_a_method=FillNAMethod.LINEAR,
        padding_value=0,
    ),
)

# set inference parameters
batch_inference_body = MultivariateBatchDetectionOptions(
    data_source=blob_url,
    top_contributor_count=10,
    start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
    end_time=datetime.strptime("2021-01-02T01:00:00Z", time_format),
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
    # print(model)
    model_status = model.model_info.status
    print("Model is {}".format(model_status))
    time.sleep(5)
if model_status == ModelStatus.READY:
    print("TRAINING COMPLETED")
    # Return the latest model id

try:
    # Detect anomaly in the same data source (but a different interval)
    result = ad_client.detect_multivariate_batch_anomaly(model_id, batch_inference_body)
    result_id = result.result_id
except HttpResponseError as e:
    error_message = e.response.json()
    print(json.dumps(error_message, indent=4))
    raise

result_status = None

# wait until inference is ready
while result_status != 'READY' and result_status != 'FAILED':
    r = ad_client.get_multivariate_batch_detection_result(result_id)
    result_status = r.summary.status
    print("Detection is {}".format(result_status))
    time.sleep(5)
if result_status == 'FAILED':
    print("Inference failed")
elif result_status == 'READY':
    anomaly_results = ad_client.get_multivariate_batch_detection_result(result_id)
    print("Result ID:\t", anomaly_results.result_id)
    print("Result status:\t", anomaly_results.summary.status)
    print("Result length:\t", len(anomaly_results.results))

    # See detailed inference result
    for r in anomaly_results.results:
        if r.value.is_anomaly:  # Check if 'isAnomaly' is True
            print(
                "timestamp: {}, is_anomaly: {:<5}, anomaly score: {:.4f}, severity: {:.4f}, contributor count: {:<4d}".format(
                    r.timestamp,
                    r.value.is_anomaly,
                    r.value.score,
                    r.value.severity,
                    len(r.value.interpretation) if r.value.is_anomaly else 0,
                )
            )
            if r.value.interpretation:
                for contributor in r.value.interpretation:
                    print(
                        "\tcontributor variable: {:<10}, contributor score: {:.4f}".format(
                            contributor.variable, contributor.contribution_score
                        )
                    )

    # view results as a table
    anomaly_results_df = pd.DataFrame([{'timestamp': x['timestamp'], **x['value']} for x in anomaly_results.results])
    # print(anomaly_results_df)

    # print merges results
    filename = os.path.basename(blob_url)
    raw_data = get_blob_data.get_data(filename)
    data = pd.merge(anomaly_results_df, raw_data, on="timestamp")
    # print(data)

    # Convert timestamp column to datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Select only timestamp and series columns
    cols_to_exclude = ['isAnomaly', 'severity', 'score', 'interpretation']
    selected_columns = [col for col in data.columns if col not in cols_to_exclude]
    df_selected = data[selected_columns]

    # remove timestamp to assign colors
    colors_selected = selected_columns[1:]

    # Get the Plotly color sequence
    colors = px.colors.qualitative.Plotly

    # Create a color map for the series
    series_color_map = {colors_selected[i]: colors[i % len(colors)] for i in range(len(colors_selected))}

    # Melt dataframe to make it long-form, which works better with Plotly
    df_melted = df_selected.melt(id_vars='timestamp', var_name='series', value_name='value')

    # Define number of rows for subplots
    num_rows = len(colors_selected)

    # Create the subplot titles dynamically
    subplot_titles = ('SERIES', 'SEVERITY') + tuple('{}'.format(name.upper()) for name in colors_selected)

    # Create the row heights list
    overlay_plot = 600
    bar_plot = 250
    solo_plots = 200
    row_heights = [overlay_plot, bar_plot] + ([solo_plots] * num_rows)

    # vertical_spacing = str((1 / ((num_rows+2) - 1))/10)
    # vertical_spacing = float(vertical_spacing[:4])

    # Set the overall height of the figure
    figure_height = sum(row_heights)

    # convert hex to rgb
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Create subplot figure with specific height ratios
    fig = make_subplots(rows=num_rows + 2,
                        cols=1,
                        shared_xaxes=False,
                        vertical_spacing=0.04,
                        # specs=[[{}], [{}]],
                        subplot_titles=subplot_titles,
                        row_heights=row_heights)

    # Plot each series on the first subplot with a unique color
    for series in colors_selected:
        fig.add_trace(go.Scatter(x=data["timestamp"],
                                 y=data[series],
                                 name=series,
                                 line_color=series_color_map[series]),
                      row=1, col=1)

    # y-axis scale facter and min and max for top plot
    y1_scale = 1.5
    y1_min = df_melted['value'].min() * y1_scale
    y1_max = df_melted['value'].max() * y1_scale

    # Iterate over rows where 'isAnomaly' is True
    for _, row in data[data['isAnomaly']].iterrows():
        interpretation = row['interpretation']
        if interpretation:  # check if interpretation is not empty
            # Sort by 'contributionScore', select the series with highest contribution
            max_contributor = max(interpretation, key=lambda x: x['contributionScore'])
            series_name = max_contributor['variable']

            # Match series name with color
            color = series_color_map.get(series_name, "white")  # default to "white" if series_name is not found in map

            # remove hash and convert hex to rgb
            rgb = hex_to_rgb(color.strip('#'))

            # add alpha channel to existing RGB color string
            rgba_color = 'rgba' + str(rgb).strip(')') + ',0.25)'

            # Add vertical line with matched color
            fig.add_shape(type='line',
                          yref='y1',  # reference to first subplot y-axis
                          x0=row['timestamp'],
                          x1=row['timestamp'],
                          y0=y1_min,
                          y1=y1_max,
                          line=dict(width=4, color=rgba_color),
                          row=1,
                          col=1)

    # Iterate over rows where 'isAnomaly' is True
    for _, row in data.iterrows():
        interpretation = row['interpretation']
        if row['isAnomaly'] and interpretation:  # check if 'isAnomaly' is True and interpretation is not empty
            severity = row['severity']
            total_contribution = sum(contributor['contributionScore'] for contributor in interpretation)
            for contributor in interpretation:
                # Retrieve the series name and its contribution score
                series_name = contributor['variable']
                contribution_score = contributor['contributionScore']

                # Calculate the percentage of contribution
                contribution_percentage = (contribution_score / total_contribution) * severity

                # Match series name with color
                color = series_color_map.get(series_name,
                                             "white")  # default to "white" if series_name is not found in map

                # Add bar as separate trace for each contributor to the anomaly
                fig.add_trace(
                    go.Bar(x=[row['timestamp']], y=[contribution_percentage], name=series_name,
                           marker=dict(color=color), showlegend=False),
                    row=2, col=1)

    # Share x-axis between the first two subplots
    fig.update_xaxes(matches='x')

    # Update layout to have stacked bars
    fig.update_layout(barmode='stack')

    # Iterate over series names
    for i, series_name in enumerate(series_color_map):
        # Create a new subplot for each series line and vertical line trace
        fig.add_trace(
            go.Scatter(x=data['timestamp'],
                       y=data[series_name],
                       name=series_name,
                       line=dict(color=series_color_map[series_name]),
                       showlegend=False),
            row=3 + i, col=1
        )

        for _, row in data[data['isAnomaly']].iterrows():
            interpretation = row['interpretation']
            if interpretation:  # check if interpretation is not empty
                # Sort by 'contributionScore', select the series with highest contribution
                max_contributor = max(interpretation, key=lambda x: x['contributionScore'])
                max_name = max_contributor['variable']

                # remove hash and convert hex to rgb
                rgb = hex_to_rgb(series_color_map[series_name].strip('#'))

                # add alpha channel to existing RGB color string
                rgba_color = 'rgba' + str(rgb).strip(')') + ',0.25)'

                # Check if 'isAnomaly' is True and the current series is the highest contributor
                if series_name == max_name:
                    # Add vertical line with the same color as the series
                    fig.add_shape(type='line',
                                  yref='y' + str(3 + i),  # reference to the y-axis of the subplot
                                  x0=row['timestamp'],
                                  x1=row['timestamp'],
                                  y0=data[series_name].min(),
                                  y1=data[series_name].max(),
                                  line=dict(width=4, color=rgba_color),
                                  row=3 + i, col=1)

    # Update y-axis ranges
    fig.update_yaxes(range=[y1_min, y1_max], row=1, col=1)
    fig.update_yaxes(range=[0, 1], row=2, col=1)

    # update theme to dark
    fig.update_layout(
        template='plotly_dark',
        height=figure_height
    )

    # Show the plot
    fig.show()
