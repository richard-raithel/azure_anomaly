from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()


def get_data(blob_name):
    try:
        # Retrieve the connection string from an environment
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

        # Create a blob service client.
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # Create a blob client using the blob's name.
        blob_client = blob_service_client.get_blob_client("uk-multi-ad-poc", blob_name)

        print("\nDownloading blob to", blob_name)

        # Download the blob to a local file
        with open(blob_name, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        # Read data into dataframe
        df = pd.read_csv(blob_name)

        return df

    except Exception as ex:
        print('Exception:')
        print(ex)
