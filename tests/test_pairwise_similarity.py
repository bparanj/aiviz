import sys
import os
import json
import pytest
import numpy as np
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.data_validation import validate_pairwise_similarity

def load_test_cases():
    test_cases_path = project_root / "data" / "pairwise_similarity_test_cases.json"
    with open(test_cases_path) as f:
        return json.load(f)["test_cases"]

@pytest.mark.parametrize("test_case", load_test_cases())
def test_validation(test_case):
    """Test validation function with various test cases."""
    is_valid, message = validate_pairwise_similarity(test_case["data"])
    assert is_valid == test_case["expected_valid"], \
        f"Test case '{test_case['name']}' failed: {message}"

def test_clustering():
    """Test clustering functionality with sample data."""
    from scipy.cluster import hierarchy
    from scipy.spatial.distance import squareform
    
    # Sample data
    data = {
        "samples": ["Doc1", "Doc2", "Doc3", "Doc4"],
        "matrix": [
            [1.00, 0.75, 0.10, 0.20],
            [0.75, 1.00, 0.15, 0.30],
            [0.10, 0.15, 1.00, 0.05],
            [0.20, 0.30, 0.05, 1.00]
        ]
    }
    
    # Convert to numpy array
    matrix = np.array(data["matrix"])
    
    # Convert similarity to distance
    distances = 1 - matrix
    np.fill_diagonal(distances, 0)
    
    # Perform clustering
    linkage = hierarchy.linkage(squareform(distances), method='ward')
    dendro = hierarchy.dendrogram(linkage, no_plot=True)
    order = dendro['leaves']
    
    # Verify clustering results
    assert len(order) == len(data["samples"]), "Clustering order length mismatch"
    assert len(set(order)) == len(order), "Duplicate indices in clustering order"
    assert all(0 <= i < len(data["samples"]) for i in order), "Invalid indices in clustering order"

def test_matrix_properties():
    """Test various matrix properties required for visualization."""
    # Valid symmetric matrix
    valid_matrix = np.array([
        [1.00, 0.75, 0.10],
        [0.75, 1.00, 0.15],
        [0.10, 0.15, 1.00]
    ])
    
    # Test symmetry
    assert np.allclose(valid_matrix, valid_matrix.T), "Matrix should be symmetric"
    
    # Test diagonal values
    assert np.allclose(np.diag(valid_matrix), 1.0), "Diagonal values should be 1.0"
    
    # Test value range
    assert np.all(valid_matrix >= 0) and np.all(valid_matrix <= 1), \
        "Matrix values should be between 0 and 1"

if __name__ == "__main__":
    pytest.main([__file__])
