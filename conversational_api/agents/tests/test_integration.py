import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch
from agents.models import Agent, ConversationalPathway

# Fixture to set up an API client for testing
@pytest.fixture
def api_client():
    return APIClient()

# Fixture for a sample agent data
@pytest.fixture
def sample_agent_data():
    return {
        'name': 'Integration Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30
    }

# Fixture for a sample conversational pathway data
@pytest.fixture
def sample_pathway_data():
    return {
        'name': 'Integration Test Pathway',
        'description': 'An integration test pathway',
        'nodes': {},
        'edges': {}
    }

# Integration Tests for AgentViewSet
@pytest.mark.django_db
def test_create_agent_with_bland_ai_integration(api_client, sample_agent_data):
    url = reverse('agent-list')

    # Mock the BlandClient interaction to simulate a successful agent creation in Bland AI
    with patch('agents.views.BlandClient.create_agent') as mock_create_agent:
        mock_create_agent.return_value = 'bland_ai_id_123'

        response = api_client.post(url, sample_agent_data, format='json')

        assert response.status_code == 201
        assert response.data['name'] == sample_agent_data['name']
        assert response.data['bland_ai_id'] == 'bland_ai_id_123'

        # Verify the agent was saved in the database
        agent = Agent.objects.get(name=sample_agent_data['name'])
        assert agent.name == 'Integration Test Agent'
        assert agent.bland_ai_id == 'bland_ai_id_123'
        assert agent.script == 'Hello'  # Assuming html_to_script strips HTML tags

@pytest.mark.django_db
def test_update_agent_with_bland_ai_integration(api_client, sample_agent_data):
    # Create an initial agent in the database
    agent = Agent.objects.create(**sample_agent_data)
    agent.bland_ai_id = '3907feac-2fe9-4da1-9175-206420df76e0'  # Assign a valid bland_ai_id for testing
    agent.save()

    url = reverse('agent-detail', args=[agent.id])
    updated_data = sample_agent_data.copy()
    updated_data['name'] = 'Updated Integration Test Agent'

    # Mock the BlandClient interaction to simulate a successful agent update in Bland AI
    with patch('agents.views.BlandClient.update_agent') as mock_update_agent:
        mock_update_agent.return_value = None  # Assume no return value for updates

        response = api_client.put(url, updated_data, format='json')

    assert response.status_code == 200
    assert response.data['name'] == updated_data['name']

    # Verify the agent was updated in the database
    agent.refresh_from_db()
    assert agent.name == 'Updated Integration Test Agent'

@pytest.mark.django_db
def test_delete_agent_with_bland_ai_integration(api_client, sample_agent_data):
    # Create an initial agent in the database
    agent = Agent.objects.create(**sample_agent_data)

    url = reverse('agent-detail', args=[agent.id])

    # Mock the BlandClient interaction to simulate a successful agent deletion in Bland AI
    with patch('agents.views.BlandClient.delete_agent') as mock_delete_agent:
        mock_delete_agent.return_value = None  # Assume no return value for deletion

        response = api_client.delete(url)

        assert response.status_code == 204

        # Verify the agent was deleted from the database
        assert Agent.objects.filter(id=agent.id).count() == 0

# Integration Tests for ConversationalPathwayViewSet
@pytest.mark.django_db
def test_create_conversational_pathway_with_bland_ai_integration(api_client, sample_pathway_data):
    url = reverse('conversationalpathway-list')

    # Mock the BlandClient interaction to simulate a successful pathway creation in Bland AI
    with patch('agents.views.BlandClient.create_conversational_pathway') as mock_create_pathway:
        mock_create_pathway.return_value = 'bland_ai_pathway_id_456'

        response = api_client.post(url, sample_pathway_data, format='json')

        assert response.status_code == 201
        assert response.data['name'] == sample_pathway_data['name']
        assert response.data['bland_ai_pathway_id'] == 'bland_ai_pathway_id_456'

        # Verify the pathway was saved in the database
        pathway = ConversationalPathway.objects.get(name=sample_pathway_data['name'])
        assert pathway.name == 'Integration Test Pathway'
        assert pathway.bland_ai_pathway_id == 'bland_ai_pathway_id_456'

@pytest.mark.django_db
def test_update_conversational_pathway_with_bland_ai_integration(api_client, sample_pathway_data):
    # Create a pathway and assign 
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)
    pathway.bland_ai_pathway_id = '564ce9cd-4ca8-494d-b5b6-7ae382d83725' #assign a valid bland_ai_pathway_id
    pathway.save()

    url = reverse('conversationalpathway-detail', args=[pathway.id])
    updated_data = sample_pathway_data.copy()
    updated_data['name'] = 'Updated Integration Test Pathway'

    with patch('agents.views.BlandClient.update_conversational_pathway') as mock_update_pathway:
        mock_update_pathway.return_value = None

        response = api_client.put(url, updated_data, format='json')

    assert response.status_code == 200
    assert response.data['name'] == updated_data['name']

    pathway.refresh_from_db()
    assert pathway.name == 'Updated Integration Test Pathway'

@pytest.mark.django_db
def test_delete_conversational_pathway_with_bland_ai_integration(api_client, sample_pathway_data):
    # Create an initial pathway in the database
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)

    url = reverse('conversationalpathway-detail', args=[pathway.id])

    # Mock the BlandClient interaction to simulate a successful pathway deletion in Bland AI
    with patch('agents.views.BlandClient.delete_conversational_pathway') as mock_delete_pathway:
        mock_delete_pathway.return_value = None  # Assume no return value for deletion

        response = api_client.delete(url)

        assert response.status_code == 204

        # Verify the pathway was deleted from the database
        assert ConversationalPathway.objects.filter(id=pathway.id).count() == 0

# Integration Tests for API Failure Scenarios
@pytest.mark.django_db
def test_create_agent_with_bland_ai_failure(api_client, sample_agent_data):
    url = reverse('agent-list')

    # Mock a failure during BlandClient agent creation
    with patch('agents.views.BlandClient.create_agent') as mock_create_agent:
        mock_create_agent.side_effect = Exception("Bland AI creation failed")

        response = api_client.post(url, sample_agent_data, format='json')

        assert response.status_code == 500  # Expect failure due to Bland AI error
        assert 'detail' in response.data

@pytest.mark.django_db
def test_update_agent_with_bland_ai_failure(api_client, sample_agent_data):
    # Create an initial agent in the database
    agent = Agent.objects.create(**sample_agent_data)

    url = reverse('agent-detail', args=[agent.id])
    updated_data = sample_agent_data.copy()
    updated_data['name'] = 'Updated Integration Test Agent'

    # Mock the BlandClient interaction to simulate a failure when updating the agent in Bland AI
    with patch('agents.views.BlandClient.update_agent') as mock_update_agent:
        mock_update_agent.side_effect = Exception("Bland AI update failed")

        response = api_client.put(url, updated_data, format='json')

        # Expect a 500 status code since the Bland AI interaction failed
        assert response.status_code == 500
        assert 'detail' in response.data
        assert response.data['detail'] == "Failed to update agent in Bland AI."

@pytest.mark.django_db
def test_delete_conversational_pathway_with_bland_ai_failure(api_client, sample_pathway_data):
    # Create an initial pathway in the database
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)

    url = reverse('conversationalpathway-detail', args=[pathway.id])

    # Mock the BlandClient interaction to simulate a failure when deleting the pathway in Bland AI
    with patch('agents.views.BlandClient.delete_conversational_pathway') as mock_delete_pathway:
        mock_delete_pathway.side_effect = Exception("Bland AI deletion failed")

        response = api_client.delete(url)

        # Expect a 500 status code since the Bland AI interaction failed
        assert response.status_code == 500
        assert 'detail' in response.data
        assert response.data['detail'] == "Error occurred while deleting the pathway in Bland AI."