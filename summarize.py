import pandas as pd


def summarize_csv(file_path, summary_file_path):
    # Load the CSV file into a pandas DataFrame
    data = pd.read_csv(file_path)

    # Generate summary statistics
    summary = data.describe(include='all')

    # Save the summary statistics to a CSV file
    summary.to_csv(summary_file_path)

    return summary


summary = summarize_csv('/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/original/SGS-Data-20230606.csv', '/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/summary.csv')
print(summary)
