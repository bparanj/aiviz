import json
import pytest
from pages.page19_Hierarchical_Clustering import validate_hierarchical_data, process_node, create_cluster_visualization
import plotly.graph_objects as go

def load_test_cases():
    with open('data/hierarchical_clustering_test_cases.json', 'r') as f:
        return json.load(f)

def test_validate_hierarchical_data_valid_cases():
    test_cases = load_test_cases()
    for case in test_cases['valid_cases']:
        errors = validate_hierarchical_data(case['data'])
        assert len(errors) == 0, f"Valid case '{case['name']}' should not have validation errors"

def test_validate_hierarchical_data_invalid_cases():
    test_cases = load_test_cases()
    for case in test_cases['invalid_cases']:
        errors = validate_hierarchical_data(case['data'])
        assert len(errors) > 0, f"Invalid case '{case['name']}' should have validation errors"
        assert any(case['expected_error'] in error for error in errors), \
            f"Expected error '{case['expected_error']}' not found in validation errors"

def test_validate_node_count():
    """Test that trees with fewer than 3 nodes are rejected."""
    small_tree = {
        "name": "Root",
        "children": [
            {"name": "Child"}
        ]
    }
    errors = validate_hierarchical_data(small_tree)
    assert any("at least 3 nodes" in error for error in errors)

def test_validate_root_requirements():
    """Test that root node must have children."""
    root_only = {"name": "Root"}
    errors = validate_hierarchical_data(root_only)
    assert any("Root node must have children" in error for error in errors)

def test_validate_empty_children():
    """Test that empty children arrays are rejected."""
    empty_children = {
        "name": "Root",
        "children": []
    }
    errors = validate_hierarchical_data(empty_children)
    assert any("Children array cannot be empty" in error for error in errors)

def test_process_node():
    test_cases = load_test_cases()
    for case in test_cases['valid_cases']:
        nodes, edges = process_node(case['data'])
        
        # Check that all nodes have required fields
        for node in nodes:
            assert 'id' in node
            assert 'label' in node
            assert 'level' in node
            assert isinstance(node['level'], int)
            assert node['level'] >= 0
        
        # Check that edges connect existing nodes
        node_ids = {node['id'] for node in nodes}
        for edge in edges:
            assert edge['from'] in node_ids
            assert edge['to'] in node_ids

def test_create_cluster_visualization():
    test_cases = load_test_cases()
    for case in test_cases['valid_cases']:
        fig = create_cluster_visualization(case['data'])
        
        # Check that figure is created correctly
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        # Check that layout contains required elements
        assert fig.layout.title.text == 'Hierarchical Clustering Visualization'
        assert fig.layout.showlegend == False
        assert fig.layout.hovermode == 'closest'
        
        # Check that axes are configured correctly
        assert fig.layout.xaxis.title.text == 'Cluster Level'
        assert fig.layout.xaxis.showgrid == False
        assert fig.layout.yaxis.showgrid == False
        assert fig.layout.yaxis.showticklabels == False

def test_visualization_colors():
    """Test that different branches have different colors."""
    test_case = {
        "name": "Color Test",
        "children": [
            {"name": "Branch A", "children": [{"name": "A1"}, {"name": "A2"}]},
            {"name": "Branch B", "children": [{"name": "B1"}, {"name": "B2"}]}
        ]
    }
    
    fig = create_cluster_visualization(test_case)
    
    # Extract colors from markers
    colors = set()
    for trace in fig.data:
        if trace.mode and 'markers' in trace.mode:
            colors.add(trace.marker.color)
    
    # Check that we have at least 2 different colors
    assert len(colors) >= 2, "Visualization should use different colors for different branches"
