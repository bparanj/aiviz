import json
import numpy as np

def validate_correlation_matrix(data):
    """Validate correlation matrix data format and values."""
    try:
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        if "features" not in data or "matrix" not in data:
            return False, "Data must contain 'features' and 'matrix' keys"
        
        features = data["features"]
        matrix = data["matrix"]
        
        if not isinstance(features, list):
            return False, "Features must be a list"
            
        if not isinstance(matrix, list):
            return False, "Matrix must be a list"
            
        if len(features) != len(matrix):
            return False, "Number of features must match matrix dimensions"
            
        for row in matrix:
            if len(row) != len(features):
                return False, "Matrix must be square"
            for val in row:
                if not isinstance(val, (int, float)):
                    return False, "Matrix values must be numbers"
                if val < -1 or val > 1:
                    return False, "Correlation values must be between -1 and 1"
                    
        return True, "Valid correlation matrix data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def validate_hyperparameter_data(data):
    """Validate hyperparameter impact data format and values."""
    try:
        if not isinstance(data, list):
            return False, "Data must be a list of objects"
            
        if len(data) < 2:
            return False, "Need at least 2 data points"
            
        for item in data:
            if not isinstance(item, dict):
                return False, "Each item must be a dictionary"
                
            if "paramValue" not in item or "metric" not in item:
                return False, "Each item must have 'paramValue' and 'metric' keys"
                
            if not isinstance(item["metric"], (int, float)):
                return False, "Metric must be a number"
                
        return True, "Valid hyperparameter data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def validate_dataset_variations(data):
    """Validate dataset variations data format and values."""
    try:
        if not isinstance(data, list):
            return False, "Data must be a list of objects"
            
        if len(data) < 2:
            return False, "Need at least 2 datasets"
            
        for item in data:
            if not isinstance(item, dict):
                return False, "Each item must be a dictionary"
                
            if "dataset" not in item or "metric" not in item:
                return False, "Each item must have 'dataset' and 'metric' keys"
                
            if not isinstance(item["metric"], (int, float)):
                return False, "Metric must be a number"
                
        return True, "Valid dataset variations data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def validate_confusion_matrix(data):
    """Validate confusion matrix data format and values."""
    try:
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        if "classes" not in data or "matrix" not in data:
            return False, "Data must contain 'classes' and 'matrix' keys"
        
        classes = data["classes"]
        matrix = data["matrix"]
        
        if not isinstance(classes, list):
            return False, "Classes must be a list"
            
        if len(classes) < 2:
            return False, "Must have at least 2 classes"
            
        if not isinstance(matrix, list):
            return False, "Matrix must be a list"
            
        if len(classes) != len(matrix):
            return False, "Number of classes must match matrix dimensions"
            
        for row in matrix:
            if len(row) != len(classes):
                return False, "Matrix must be square"
            for val in row:
                if not isinstance(val, (int, float)):
                    return False, "Matrix values must be numbers"
                if val < 0:
                    return False, "Matrix values must be non-negative"
                    
        return True, "Valid confusion matrix data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def load_json_data(json_str):
    """Load and parse JSON data."""
    try:
        return json.loads(json_str)
    except Exception as e:
        return None, f"Error parsing JSON: {str(e)}"
