import csv
from collections import Counter


def convert_to_ducktype(string):
    # Convert the string to duck type
    ducktype = string.lower().title()

    # Remove spaces from the string
    new_string = ducktype.replace(" ", "")

    return new_string


def find_top_values(csv_file, column_name):
    # Read the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    # Extract values from the specified column
    column_values = [row[column_name] for row in rows]

    # Find the top 3 values with the highest occurrences
    top_values = Counter(column_values).most_common(3)
    top_values = [value[0] for value in top_values]

    # Print the values and their occurrences
    for value in top_values:
        count = column_values.count(value)
        print(f"Value: {value}, Occurrences: {count}")

    # Filter rows based on the top values
    filtered_rows = [row for row in rows if row[column_name] in top_values]

    # Save each filtered row to a new CSV file
    for value in top_values:
        # for row in filtered_rows:
            # if row[column_name] == value:
        #         customerName = row['CustomerName']
        #         customer = convert_to_ducktype(customerName)
        #         siteName = row['SiteName']
        #         site = convert_to_ducktype(siteName)
        #         productName = row['ProductName']
        #         product = convert_to_ducktype(productName)
        # filename = f"/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/top_n/{customer}_{site}_{product}_{value}.csv"
        product = convert_to_ducktype(value)
        filename = f"/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/top_n/{product}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows([row for row in filtered_rows if row[column_name] == value])

        print(f"{filename}.csv created successfully")


# Example usage
csv_file = '/home/rraithel/drv1/pythonProjects/MultivariateAnomalyDetection/data/original/SGS-Data-20230606.csv'
column_name = 'ProductName'
find_top_values(csv_file, column_name)
