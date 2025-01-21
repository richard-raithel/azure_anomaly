# Azure Anomaly Detection Workflow

## Overview

This project provides a comprehensive workflow for detecting anomalies in datasets using Azure Cognitive Services for Anomaly Detection. The workflow includes scripts for data preprocessing, anomaly detection, visualization, and summarization. It supports both univariate and multivariate anomaly detection.

---

## Features
- **Data Preprocessing**:
  - Normalize and filter raw data (`filter_data.py`, `filter_data_normalize.py`).
  - Extract frequent patterns (`find_frequent.py`).
  - Fetch data from Azure Blob Storage (`get_blob_data.py`).

- **Anomaly Detection**:
  - Univariate anomaly detection (`sample_univariate_detect.py`).
  - Multivariate anomaly detection with training and inference (`multivariate_train.py`, `multivariate_inference_and_plot.py`).

- **Visualization**:
  - Plot results for single products (`plot_single_product.py`).
  - Generate summary reports of anomalies (`summarize.py`).

- **Output**:
  - Anomalies and outliers identified and saved as CSV files (e.g., `BellBorateOil_outliers.csv`, `summary.csv`).

---

## Directory Structure
- **data/**: Directory for storing raw and processed datasets.
- **detect_outliers.py**: Main script for anomaly detection.
- **filter_data.py**: Filters data for noise reduction.
- **filter_data_normalize.py**: Normalizes data for better anomaly detection.
- **find_frequent.py**: Identifies frequent patterns in the dataset.
- **get_blob_data.py**: Downloads data from Azure Blob Storage.
- **model_id.txt**: Stores the model ID for multivariate detection.
- **multivariate_data.csv**: Sample multivariate dataset.
- **multivariate_train.py**: Trains a model for multivariate anomaly detection.
- **multivariate_inference_and_plot.py**: Infers anomalies and plots the results.
- **plot_single_product.py**: Visualizes anomaly results for a single product.
- **requirements.txt**: Lists required Python packages.
- **sample_multivariate_detect.py**: Sample script for multivariate anomaly detection.
- **sample_univariate_detect.py**: Sample script for univariate anomaly detection.
- **summarize.py**: Summarizes anomaly detection results.
- **summary.csv**: Summary of anomalies detected.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Azure subscription with Anomaly Detector resource set up
- Azure Blob Storage for data storage

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/azure-anomaly-detection-workflow.git
   cd azure-anomaly-detection-workflow
