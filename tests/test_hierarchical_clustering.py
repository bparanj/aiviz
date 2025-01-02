import json
import pytest
from pages.nineteen_Hierarchical_Clustering import validate_node, process_node, create_cluster_visualization
import plotly.graph_objects as go

def load_test_cases():
    with open('data/hierarchical_clustering_test_cases.json', 'r') as f:
        return json.load(f)

def test_validate_node_valid_cases():
    test_cases = load_test_cases()
    for case in test_cases['valid_cases']:
        errors = validate_node(case['data'])
        assert len(errors) == 0, f"Valid case '{case['name']}' should not have validation errors"

def test_validate_node_invalid_cases():
    test_cases = load_test_cases()
    for case in test_cases['invalid_cases']:
        errors = validate_node(case['data'])
        assert len(errors) > 0, f"Invalid case '{case['name']}' should have validation errors"
        assert any(case['expected_error'] in error for error in errors), \
            f"Expected error '{case['expected_error']}' not found in validation errors"

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
