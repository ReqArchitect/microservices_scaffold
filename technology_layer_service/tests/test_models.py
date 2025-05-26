import pytest
from technology_layer_service.app.models import Node
from datetime import datetime

def test_node_creation():
    node = Node(name='Test Node', description='A test node')
    assert node.name == 'Test Node'
    assert node.description == 'A test node'
    assert isinstance(node.created_at, datetime) or node.created_at is None

def test_node_to_dict():
    node = Node(name='Test Node', description='A test node')
    d = node.to_dict()
    assert d['name'] == 'Test Node'
    assert d['description'] == 'A test node'
    assert 'created_at' in d

def test_node_required_fields():
    with pytest.raises(TypeError):
        Node() 