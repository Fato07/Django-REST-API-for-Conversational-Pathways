import pytest
from rest_framework.test import APIClient

@pytest.fixture
def sample_agent_data():
    return {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30
    }
    
@pytest.fixture
def sample_pathway_data():
    return {
        'name': 'End-to-End Test Pathway',
        'description': 'An end-to-end test pathway',
        'nodes': {},
        'edges': {}
    }

# Fixture for APIClient
@pytest.fixture
def api_client():
    return APIClient()

