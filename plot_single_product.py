import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

# Read the CSV data
data_orig = pd.read_csv('/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/BellBorateOil_outliers.csv')

# Exclude the last 3 columns
data = data_orig.iloc[:, :-3]

# Strip brackets and quotes from 'Outliers' column
data_orig['Outliers'] = data_orig['Outliers'].str.replace(r"'", '')

# Calculate the number of subplots
num_subplots = (data.shape[1] + 1) // 2

# Create a new column to indicate outliers
data['IsOutlier'] = False

# Iterate over each row and set 'IsOutlier' value
for idx, row in data.iterrows():
    try:
        outliers = row['Outliers'].split(',')
    except KeyError:
        outliers = ''
        pass
    for column in data.columns:
        if column in outliers:
            data.at[idx, 'IsOutlier'] = True

# Create subplots
fig = make_subplots(rows=num_subplots, cols=2, subplot_titles=data.columns)

# Iterate over each column and create boxplots with points
for i, column in enumerate(data.columns):
    # Calculate the subplot position
    row = (i // 2) + 1
    col = (i % 2) + 1

    # Create the boxplot with points and color outliers red
    fig.add_trace(px.box(data, y=column, points='all', color='IsOutlier').data[0], row=row, col=col)

# Update the layout
fig.update_layout(height=num_subplots * 400, showlegend=False)

# Show the plot
fig.show()
