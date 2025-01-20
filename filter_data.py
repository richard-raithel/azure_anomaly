import os
import pandas as pd
import numpy as np
from datetime import datetime


def convert_timestamp(timestamp):
    # Assuming the timestamp format is "%d/%m/%Y %H:%M:%S"
    parsed_timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M:%S")
    converted_timestamp = parsed_timestamp.strftime("%Y-%m-%dT00:00:00Z")
    return converted_timestamp


def process_csv(input_file, output_file):
    # Read csv file into DataFrame
    df_original = pd.read_csv(input_file)

    # # Exclude rows where 'Status' is 'Serious'
    # df = df[df['Status'] != 'Serious']

    # Filter the necessary columns
    remaining_columns = set(list(range(18, 40)) + [41] + [43] + [58] + [60])  # Update column indices based on your requirement
    df = df_original.iloc[:, list(remaining_columns)]

    # Append column with original index 12 at the end of the DataFrame
    df = pd.concat([df, df_original.iloc[:, 12]], axis=1)
    print(df)

    # Create a subset of df excluding the 'Status' column
    subset = df.drop(columns=['Status', 'Interpretation'])

    # Find the indices of the rows where all values are null in the subset
    empty_rows = subset[subset.isnull().all(axis=1)].index

    # Drop these rows from the original dataframe
    df = df.drop(empty_rows)

    # # Convert strings that can be interpreted as numbers, ignore the rest
    # df = df.apply(pd.to_numeric, errors='coerce')
    #
    # # Remove any empty rows
    # df = df.dropna(how='all')
    #
    # # Calculate the average of each column, ignoring NaN values
    # averages = df.mean()
    #
    # # Round the averages to 1 decimal place
    # averages_rounded = averages.round(1)
    #
    # # Print each column name with its average
    # for col_name, average in averages_rounded.items():
    #     print(f"Average of column '{col_name}': {average}")
    #
    # # Append the rounded averages to the DataFrame
    # df = df._append(averages_rounded, ignore_index=True)

    # Write the DataFrame to csv
    df.to_csv(output_file, index=False)

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
