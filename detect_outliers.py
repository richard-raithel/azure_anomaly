import pandas as pd
import numpy as np
from scipy import stats

# Load dataset
df = pd.read_csv('/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/filtered/BellBorateOil.csv')

# Replace missing values with NaN
df = df.replace("", float("NaN"))

# Create a new dataframe excluding 'Status' column for calculating Z-scores
df_for_zscore = df.drop(['Status', 'Interpretation'], axis=1)

# Convert strings to numbers, ignore errors for non-convertible strings
df_for_zscore = df_for_zscore.apply(pd.to_numeric, errors='coerce')

# Calculate Z-scores
z_scores = stats.zscore(df_for_zscore)

# Define a threshold
threshold = 3

# Get absolute Z-scores greater than the threshold
outliers = np.abs(z_scores) > threshold

# Initialize dictionary to store rows containing outliers and corresponding columns
outlier_dict = {}

# Iterate over the DataFrame to identify the variables (columns) and the row indices of outliers
for column in df_for_zscore.columns:
    if outliers[df_for_zscore[column].name].any():
        outlier_rows = np.where(outliers[df_for_zscore[column].name])[0]
        for row in outlier_rows:
            if row in outlier_dict:
                outlier_dict[row].append(column)
            else:
                outlier_dict[row] = [column]

# Add an 'Outliers' column in the DataFrame,
# By default, it is filled with empty lists
df['Outliers'] = [[] for _ in range(len(df))]

# Iterate over the outlier_dict and fill the 'Outliers' column
for row in outlier_dict:
    df.at[row, 'Outliers'] = outlier_dict[row]

# Get a list of the column names
cols = df.columns.tolist()

# Swap the last two column names
cols[-2], cols[-1] = cols[-1], cols[-2]

# Reindex the DataFrame
df = df[cols]

# Write DataFrame with 'Outliers' column to a new CSV file
df.to_csv('BellBorateOil_outliers.csv', index=False)

# Print rows and corresponding outlier columns
for row in sorted(outlier_dict.keys()):
    print(f"Row index: {row}, Columns: {df.at[row, 'Outliers']}")

# Calculate column averages excluding outliers
df_no_outliers = df[~outliers.any(axis=1)].drop(['Status', 'Interpretation', 'Outliers'], axis=1)
averages_no_outliers = df_no_outliers.mean(skipna=True)

# Print column averages excluding outliers
print("\nColumn averages excluding outliers:")
for column in averages_no_outliers.index:
    print(f"{column}: {averages_no_outliers[column]:.1f}")
