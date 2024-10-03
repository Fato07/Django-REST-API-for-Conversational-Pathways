import pytest
from django.urls import reverse
from unittest.mock import patch
from agents.models import Agent, ConversationalPathway

# End-to-End Test: Create Agent with Bland AI Integration
@pytest.mark.django_db
def test_create_agent_e2e(api_client, sample_agent_data):
    url = reverse('agent-list')

    # Mock the BlandClient to simulate successful agent creation in Bland AI
    with patch('agents.views.BlandClient.create_agent') as mock_create_agent:
        mock_create_agent.return_value = 'bland_ai_id_123'  # Mock return value for Bland AI agent ID

        response = api_client.post(url, sample_agent_data, format='json')

    assert response.status_code == 201  # Successful creation
    assert response.data['bland_ai_id'] == 'bland_ai_id_123'

    # Verify that the agent is created in the database
    agent = Agent.objects.get(name=sample_agent_data['name'])
    assert agent.bland_ai_id == 'bland_ai_id_123'
    assert agent.prompt == sample_agent_data['prompt']


# End-to-End Test: Update Agent with Bland AI Integration
@pytest.mark.django_db
def test_update_agent_e2e(api_client, sample_agent_data):
    # First, create the agent
    agent = Agent.objects.create(**sample_agent_data)
    agent.bland_ai_id = 'bland_ai_id_123'
    agent.save()

    url = reverse('agent-detail', args=[agent.id])
    updated_data = sample_agent_data.copy()
    updated_data['name'] = 'Updated End-to-End Test Agent'

    # Mock the BlandClient to simulate successful update in Bland AI
    with patch('agents.views.BlandClient.update_agent') as mock_update_agent:
        mock_update_agent.return_value = None  # No return value for updates

        response = api_client.put(url, updated_data, format='json')

    assert response.status_code == 200
    assert response.data['name'] == 'Updated End-to-End Test Agent'

    # Verify that the agent is updated in the database
    agent.refresh_from_db()
    assert agent.name == 'Updated End-to-End Test Agent'


# End-to-End Test: Delete Agent with Bland AI Integration
@pytest.mark.django_db
def test_delete_agent_e2e(api_client, sample_agent_data):
    # First, create the agent
    agent = Agent.objects.create(**sample_agent_data)
    agent.bland_ai_id = 'bland_ai_id_123'
    agent.save()

    url = reverse('agent-detail', args=[agent.id])

    # Mock the BlandClient to simulate successful deletion in Bland AI
    with patch('agents.views.BlandClient.delete_agent') as mock_delete_agent:
        mock_delete_agent.return_value = None  # No return value for deletion

        response = api_client.delete(url)

    assert response.status_code == 204  # No content after successful deletion

    # Verify that the agent is deleted from the database
    assert not Agent.objects.filter(id=agent.id).exists()


# End-to-End Test: Create Conversational Pathway with Bland AI Integration
@pytest.mark.django_db
def test_create_conversational_pathway_e2e(api_client, sample_pathway_data):
    url = reverse('conversationalpathway-list')

    # Mock the BlandClient to simulate successful pathway creation in Bland AI
    with patch('agents.views.BlandClient.create_conversational_pathway') as mock_create_pathway:
        mock_create_pathway.return_value = 'bland_ai_pathway_id_123'  # Mock return value for Bland AI pathway ID

        response = api_client.post(url, sample_pathway_data, format='json')

    assert response.status_code == 201  # Successful creation
    assert response.data['bland_ai_pathway_id'] == 'bland_ai_pathway_id_123'

    # Verify that the pathway is created in the database
    pathway = ConversationalPathway.objects.get(name=sample_pathway_data['name'])
    assert pathway.bland_ai_pathway_id == 'bland_ai_pathway_id_123'


# End-to-End Test: Update Conversational Pathway with Bland AI Integration
@pytest.mark.django_db
def test_update_conversational_pathway_e2e(api_client, sample_pathway_data):
    # First, create the pathway
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)
    pathway.bland_ai_pathway_id = 'bland_ai_pathway_id_123'
    pathway.save()

    url = reverse('conversationalpathway-detail', args=[pathway.id])
    updated_data = sample_pathway_data.copy()
    updated_data['name'] = 'Updated End-to-End Test Pathway'

    # Mock the BlandClient to simulate successful pathway update in Bland AI
    with patch('agents.views.BlandClient.update_conversational_pathway') as mock_update_pathway:
        mock_update_pathway.return_value = None  # No return value for updates

        response = api_client.put(url, updated_data, format='json')

    assert response.status_code == 200
    assert response.data['name'] == 'Updated End-to-End Test Pathway'

    # Verify that the pathway is updated in the database
    pathway.refresh_from_db()
    assert pathway.name == 'Updated End-to-End Test Pathway'


# End-to-End Test: Delete Conversational Pathway with Bland AI Integration
@pytest.mark.django_db
def test_delete_conversational_pathway_e2e(api_client, sample_pathway_data):
    # First, create the pathway
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)
    pathway.bland_ai_pathway_id = 'bland_ai_pathway_id_123'
    pathway.save()

    url = reverse('conversationalpathway-detail', args=[pathway.id])

    # Mock the BlandClient to simulate successful deletion in Bland AI
    with patch('agents.views.BlandClient.delete_conversational_pathway') as mock_delete_pathway:
        mock_delete_pathway.return_value = None  # No return value for deletion

        response = api_client.delete(url)

    assert response.status_code == 204  # No content after successful deletion

    # Verify that the pathway is deleted from the database
    assert not ConversationalPathway.objects.filter(id=pathway.id).exists()