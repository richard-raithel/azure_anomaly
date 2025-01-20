import csv
import os
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


def convert_timestamp(timestamp):
    # Assuming the timestamp format is "%d/%m/%Y %H:%M:%S"
    parsed_timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S")
    converted_timestamp = parsed_timestamp.strftime("%Y-%m-%dT00:00:00Z")
    return converted_timestamp


def process_csv(input_file, output_file):
    with open(input_file, 'r') as csv_input:
        reader = csv.reader(csv_input)
        rows = list(reader)

        # Extract header row
        header_row = rows[0]

        # Filter column names based on the remaining columns
        remaining_columns = set([7] + list(range(18, 42)) + [43])  # Update column indices based on your requirement
        filtered_header = [header_row[i].lower() for i in remaining_columns]

        # Remove unwanted columns and convert timestamp
        rows = [[convert_timestamp(row[7])] + row[18:43] for row in rows[1:]]

        # Insert filtered header row back to the processed rows
        rows.insert(0, filtered_header)

        # Convert rows to a NumPy array
        np_rows = np.array(rows)

        # Remove empty rows (except for the timestamp column)
        non_empty_rows = np_rows[~np.all(np_rows[:, 1:] == '', axis=1)]

        # Exclude timestamp column and normalize remaining columns
        data = non_empty_rows[1:, 1:]  # Exclude header and timestamp column
        df = pd.DataFrame(data)
        df.replace("", np.nan, inplace=True)
        df = df.astype(float)
        df.fillna(df.mean(), inplace=True)
        data = df.values

        scaler = MinMaxScaler()
        data_normalized = scaler.fit_transform(data)

        # Combine timestamp column and normalized data
        final_rows = np.column_stack((non_empty_rows[1:, 0], data_normalized))  # Include timestamps
        final_rows = np.vstack((non_empty_rows[0], final_rows))  # Include header

        with open(output_file, 'w', newline='') as csv_output:
            writer = csv.writer(csv_output)
            writer.writerows(final_rows)

        print(f"Processed CSV file '{input_file}' has been saved as '{output_file}'")


# Directory containing CSV files
directory = '/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/top_n/'  # Replace with the directory path

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        input_file = os.path.join(directory, filename)
        output_file = os.path.join("/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/filtered/",
                                   filename)

        process_csv(input_file, output_file)
