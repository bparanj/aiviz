# ML Visualization Dashboard

A Streamlit-based dashboard for visualizing various machine learning metrics and relationships.

## Features

- **Hyperparameter Impact**: Visualize how different hyperparameter settings affect model performance
- **Dataset Variations**: Compare model performance across different dataset splits
- **Correlation Matrix**: Explore feature correlations in your data

## Installation

1. Clone this repository
2. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
streamlit run app.py
```

## Data Format

### Hyperparameter Impact
```json
{
  "data": [
    {"paramValue": "10 trees", "metric": 0.75},
    {"paramValue": "50 trees", "metric": 0.82}
  ]
}
```

### Dataset Variations
```json
{
  "data": [
    {"dataset": "Training", "metric": 0.90},
    {"dataset": "Validation", "metric": 0.85}
  ]
}
```

### Correlation Matrix
```json
{
  "features": ["Feature1", "Feature2"],
  "matrix": [
    [1.00, 0.65],
    [0.65, 1.00]
  ]
}
```

## Deployment

To deploy on Streamlit Cloud:

1. Fork this repository
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign up and connect your GitHub account
4. Deploy the app by selecting the repository and main file (app.py)

## Sample Data

Sample JSON files are provided in the `data/` directory for testing each visualization.
