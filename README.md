# AWS Savings Plan Calculator

This project lets us explore and understand AWS savings plans and analyzes cost benefits based on usage commitments and past usage.

## Project Overview

This project provides an API to analyze AWS EC2 usage data and calculate potential savings using AWS Savings Plans. It includes functionality to:
- Interactive notebook for exploring savings scenarios
- Calculate savings based on a given commitment amount
- Find optimal commitment amounts for maximum savings


## Project Structure

```
.
├── aws_savings/
│   ├── data/              # Raw data files
│   │   ├── currfile.csv          # EC2 instance usage history
│   │   ├── head_curr.csv         # Sample of usage data for testing
│   │   └── savingsplanrates.csv  # AWS Savings Plan rates
│   ├── models/            # Pydantic models for API requests
│   ├── services/          # Business logic for savings calculations
│   ├── utils/             # Utility functions
│   └── main.py           # FastAPI application entry point
└── notebooks/            # Interactive analysis notebooks
```

## Data Files

The `aws_savings/data/` directory contains the following files:

- `currfile.csv`: Contains historical EC2 instance usage data with columns for operation type, usage amount, and on-demand rates
- `head_curr.csv`: A smaller subset of the usage data, useful for testing and development
- `savingsplanrates.csv`: AWS Savings Plan rates for different instance types and operations

## Installation

Install dependencies:
   ```

Install dependencies:
   ```bash
   poetry install
   ```

## Usage

1. Start the API server (choose one of these options):
   ```bash
   # Option 1: Run directly with Poetry
   poetry run python aws_savings/main.py

   # Option 2: Run with uvicorn through Poetry
   poetry run uvicorn aws_savings.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Activate virtual environment (for development):
   ```bash
   poetry shell
   ```

2. API Endpoints:
   - POST `/calculate-savings`: Calculate savings for a given commitment amount
   - POST `/find-optimal-savings`: Find the optimal commitment amount

3. Interactive Analysis:
   - Open the notebook in `notebooks/calculate_per_instance_interactive.ipynb`
   - Use the interactive widgets to explore different savings scenarios

## API Examples

Calculate savings for a specific commitment:
```json
POST /calculate-savings
{
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-01-14T00:00:00Z",
    "commitment_amount": 100
}
```

Find optimal commitment amount:
```json
POST /find-optimal-savings
{
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2023-01-14T00:00:00Z",
    "tolerance": 0.5
}
```
