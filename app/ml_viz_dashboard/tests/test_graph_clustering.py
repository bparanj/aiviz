import sys
import os
import json
import pytest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from pages.ten_graph_clustering import validate_data, create_network_graph, detect_communities

def load_test_cases():
    """Load test cases from JSON file."""
    test_cases_path = project_root / "data" / "graph_clustering_test_cases.json"
    with open(test_cases_path, 'r') as f:
        return json.load(f)

test_cases = load_test_cases()

def test_valid_data_validation():
    """Test validation with valid data."""
    assert validate_data(test_cases["valid_case"]) == True

def test_invalid_duplicate_id():
    """Test validation catches duplicate node IDs."""
    assert validate_data(test_cases["invalid_duplicate_id"]) == False

def test_invalid_missing_node():
    """Test validation catches missing node references in links."""
    assert validate_data(test_cases["invalid_missing_node"]) == False

def test_invalid_weight():
    """Test validation catches invalid weight type."""
    assert validate_data(test_cases["invalid_weight"]) == False

def test_minimal_valid_case():
    """Test validation accepts minimal valid case."""
    assert validate_data(test_cases["minimal_valid"]) == True

def test_network_graph_creation():
    """Test network graph creation with valid data."""
    G = create_network_graph(test_cases["valid_case"])
    assert len(G.nodes()) == 8  # Number of nodes
    assert len(G.edges()) == 9  # Number of links
    
    # Check node labels
    assert G.nodes["A1"]["label"] == "Team Lead"
    
    # Check edge weights
    assert G.edges[("A1", "A2")]["weight"] == 5.0

def test_community_detection():
    """Test community detection functionality."""
    G = create_network_graph(test_cases["valid_case"])
    communities = detect_communities(G)
    
    # Verify all nodes are assigned to communities
    assert len(communities) == len(G.nodes())
    
    # Verify nodes in same cluster have same community ID
    assert communities["A1"] == communities["A2"]  # Team members should be in same community
    assert communities["B1"] == communities["B2"]  # Design team should be in same community
