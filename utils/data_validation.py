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

def validate_attention_map_data(data):
    """Validate attention map data format and values."""
    try:
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        if "tokens" not in data or "attentionMaps" not in data:
            return False, "Data must contain 'tokens' and 'attentionMaps' keys"
        
        tokens = data["tokens"]
        attention_maps = data["attentionMaps"]
        
        if not isinstance(tokens, list) or len(tokens) == 0:
            return False, "Tokens must be a non-empty list"
            
        if not isinstance(attention_maps, list):
            return False, "AttentionMaps must be a list"
            
        tokens_count = len(tokens)
        
        for layer in attention_maps:
            if not isinstance(layer, dict):
                return False, "Each layer must be a dictionary"
                
            if "layerIndex" not in layer or "heads" not in layer:
                return False, "Each layer must have 'layerIndex' and 'heads'"
                
            if not isinstance(layer["heads"], list):
                return False, "Layer heads must be a list"
                
            for head in layer["heads"]:
                if not isinstance(head, dict):
                    return False, "Each head must be a dictionary"
                    
                if "headIndex" not in head or "matrix" not in head:
                    return False, "Each head must have 'headIndex' and 'matrix'"
                    
                matrix = head["matrix"]
                if not isinstance(matrix, list):
                    return False, "Matrix must be a list"
                    
                if len(matrix) != tokens_count:
                    return False, "Matrix dimensions must match number of tokens"
                    
                for row in matrix:
                    if not isinstance(row, list) or len(row) != tokens_count:
                        return False, "Matrix must be square with dimensions matching tokens"
                        
                    for val in row:
                        if not isinstance(val, (int, float)):
                            return False, "Matrix values must be numbers"
                        if val < 0 or val > 1:
                            return False, "Matrix values must be between 0 and 1"
                            
        return True, "Valid attention map data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def validate_feature_interactions(data):
    """Validate feature interactions data format and values."""
    try:
        if not isinstance(data, dict):
            return False, "Data must be a dictionary"
        
        if "features" not in data or "matrix" not in data:
            return False, "Data must contain 'features' and 'matrix' keys"
        
        features = data["features"]
        matrix = data["matrix"]
        
        if not isinstance(features, list) or len(features) < 2:
            return False, "Features must be a list with at least 2 features"
            
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
                if val < 0 or val > 1:
                    return False, "Matrix values must be between 0 and 1"
                    
        return True, "Valid feature interactions data"
    except Exception as e:
        return False, f"Error validating data: {str(e)}"

def validate_pairwise_similarity(data):
    """
    Validate pairwise similarity data format and values.
    
    Args:
        data (dict): Dictionary containing samples and similarity matrix
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
        
    Validation rules:
    1. Data must be a dictionary with 'samples' and 'matrix' keys
    2. Samples must be a list with at least 2 items
    3. Matrix must be square with dimensions matching samples length
    4. Matrix values must be between 0.0 and 1.0
    5. Diagonal values must be 1.0 (self-similarity)
    """
    try:
        # Check data type
        if not isinstance(data, dict):
            return False, "Invalid data format: Expected a dictionary with 'samples' and 'matrix' keys"
        
        # Check required keys
        if "samples" not in data or "matrix" not in data:
            return False, "Missing required keys: Both 'samples' and 'matrix' must be present"
        
        samples = data["samples"]
        matrix = data["matrix"]
        
        # Validate samples
        if not isinstance(samples, list):
            return False, "Invalid samples format: Expected a list of sample identifiers"
            
        if len(samples) < 2:
            return False, "Insufficient samples: Need at least 2 samples for meaningful comparison"
            
        # Check for duplicate samples
        if len(samples) != len(set(samples)):
            return False, "Invalid samples: Contains duplicate sample identifiers"
            
        # Validate matrix structure
        if not isinstance(matrix, list):
            return False, "Invalid matrix format: Expected a list of lists"
            
        if len(matrix) != len(samples):
            return False, f"Matrix dimension mismatch: Expected {len(samples)} rows, got {len(matrix)}"
            
        # Validate matrix values and symmetry
        for i, row in enumerate(matrix):
            if not isinstance(row, list):
                return False, f"Invalid matrix row {i}: Expected a list"
                
            if len(row) != len(samples):
                return False, f"Matrix row {i} dimension mismatch: Expected {len(samples)} columns, got {len(row)}"
                
            for j, val in enumerate(row):
                # Check numeric values
                if not isinstance(val, (int, float)):
                    return False, f"Invalid value at position ({i},{j}): Expected a number, got {type(val).__name__}"
                    
                # Check value range
                if val < 0.0 or val > 1.0:
                    return False, f"Invalid similarity value at position ({i},{j}): {val} - Must be between 0.0 and 1.0"
                    
                # Check symmetry
                if matrix[j][i] != val:
                    return False, f"Matrix not symmetric: Value at ({i},{j}) differs from ({j},{i})"
                    
                # Check diagonal values
                if i == j and val != 1.0:
                    return False, f"Invalid self-similarity at position ({i},{i}): Must be 1.0"
                
        return True, "Valid pairwise similarity data"
    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}"

def validate_json_structure(data, required_fields=None):
    """
    Validate that the input data is a dictionary and contains required fields of specified types.
    
    Args:
        data: The data to validate
        required_fields: Optional dictionary mapping field names to their required types
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    if not isinstance(data, dict):
        return False
        
    if required_fields:
        for field, field_type in required_fields.items():
            if field not in data:
                return False
            if not isinstance(data[field], field_type):
                return False
                
    return True

def load_json_data(json_str):
    """Load and parse JSON data."""
    try:
        return json.loads(json_str)
    except Exception as e:
        return None, f"Error parsing JSON: {str(e)}"

def validate_neural_network_topology(data):
    """
    Validate neural network topology data format and structure.
    
    Args:
        data (dict): Dictionary containing the hierarchical neural network topology
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
        
    Validation rules:
    1. Data must be a dictionary with 'name' and 'children' keys
    2. Each node must have a 'name' (string) field
    3. Each node must have a 'children' (list) field
    4. The 'type' field is optional but must be a string if present
    5. Each child node must follow the same validation rules recursively
    """
    try:
        def validate_node(node, path="root"):
            # Check if node is a dictionary
            if not isinstance(node, dict):
                return False, f"Invalid node at {path}: Expected a dictionary"
            
            # Check required fields
            if "name" not in node:
                return False, f"Missing 'name' field at {path}"
            if "children" not in node:
                return False, f"Missing 'children' field at {path}"
                
            # Validate field types
            if not isinstance(node["name"], str):
                return False, f"Invalid 'name' at {path}: Must be a string"
            if not isinstance(node["children"], list):
                return False, f"Invalid 'children' at {path}: Must be a list"
                
            # Validate optional type field
            if "type" in node and not isinstance(node["type"], str):
                return False, f"Invalid 'type' at {path}: Must be a string"
                
            # Recursively validate children
            for i, child in enumerate(node["children"]):
                child_path = f"{path}.children[{i}]"
                is_valid, message = validate_node(child, child_path)
                if not is_valid:
                    return False, message
            
            return True, "Valid node structure"
        
        # Start validation from root
        return validate_node(data)
    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}"
