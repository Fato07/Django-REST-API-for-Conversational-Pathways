import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from agents.models import Agent, ConversationalPathway

@pytest.mark.django_db
def test_create_agent(api_client, sample_agent_data):
    url = reverse('agent-list')  # Assuming this is your agent-list route name
    
    with patch('agents.views.BlandClient.create_agent') as mock_create_agent:
        mock_create_agent.return_value = 'bland_ai_id_123'

        response = api_client.post(url, sample_agent_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == sample_agent_data['name']
        assert response.data['bland_ai_id'] == 'bland_ai_id_123'

        # Verify agent was created in the database
        agent = Agent.objects.get(name=sample_agent_data['name'])
        assert agent.name == sample_agent_data['name']
        assert agent.bland_ai_id == 'bland_ai_id_123'

@pytest.mark.django_db
def test_update_agent(api_client, sample_agent_data):
    # Create an agent for updating
    agent = Agent.objects.create(**sample_agent_data)

    url = reverse('agent-detail', args=[agent.id])
    updated_data = sample_agent_data.copy()
    updated_data['name'] = 'Updated Agent Name'
    
    with patch('agents.views.BlandClient.update_agent') as mock_update_agent:
        mock_update_agent.return_value = None  # Assume no return value for updates
        
        response = api_client.put(url, updated_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == updated_data['name']
        
        # Verify agent was updated in the database
        agent.refresh_from_db()
        assert agent.name == updated_data['name']

@pytest.mark.django_db
def test_delete_agent(api_client, sample_agent_data):
    # Create an agent for deletion
    agent = Agent.objects.create(**sample_agent_data)

    url = reverse('agent-detail', args=[agent.id])
    
    with patch('agents.views.BlandClient.delete_agent') as mock_delete_agent:
        mock_delete_agent.return_value = None  # Assume no return value for deletes
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify agent was deleted from the database
        assert Agent.objects.filter(id=agent.id).count() == 0

@pytest.fixture(autouse=True)
def clear_database():
    Agent.objects.all().delete()
    ConversationalPathway.objects.all().delete()
    
@pytest.mark.django_db
def test_get_agent_list(api_client, sample_agent_data):
    Agent.objects.create(**sample_agent_data)
    Agent.objects.create(name='Another Agent', prompt='Hi', voice='default_voice', max_duration=20)

    url = reverse('agent-list')
    response = api_client.get(url, format='json')

    assert response.status_code == 200
    assert response.data['count'] == 2  # Adjust according to pagination

@pytest.mark.django_db
def test_get_single_agent(api_client, sample_agent_data):
    # Create an agent
    agent = Agent.objects.create(**sample_agent_data)

    url = reverse('agent-detail', args=[agent.id])

    response = api_client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == agent.name

# Tests for ConversationalPathwayViewSet

@pytest.mark.django_db
def test_create_conversational_pathway(api_client, sample_pathway_data):
    url = reverse('conversationalpathway-list')  # Assuming this is your conversationalpathway-list route name
    
    with patch('agents.views.BlandClient.create_conversational_pathway') as mock_create_pathway:
        mock_create_pathway.return_value = 'bland_ai_pathway_id_456'

        response = api_client.post(url, sample_pathway_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == sample_pathway_data['name']
        assert response.data['bland_ai_pathway_id'] == 'bland_ai_pathway_id_456'

        # Verify pathway was created in the database
        pathway = ConversationalPathway.objects.get(name=sample_pathway_data['name'])
        assert pathway.name == sample_pathway_data['name']
        assert pathway.bland_ai_pathway_id == 'bland_ai_pathway_id_456'

@pytest.mark.django_db
def test_update_conversational_pathway(api_client, sample_pathway_data):
    # Create a pathway for updating
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)

    url = reverse('conversationalpathway-detail', args=[pathway.id])
    updated_data = sample_pathway_data.copy()
    updated_data['name'] = 'Updated Pathway Name'
    
    with patch('agents.views.BlandClient.update_conversational_pathway') as mock_update_pathway:
        mock_update_pathway.return_value = None  # Assume no return value for updates
        
        response = api_client.put(url, updated_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == updated_data['name']
        
        # Verify pathway was updated in the database
        pathway.refresh_from_db()
        assert pathway.name == updated_data['name']

@pytest.mark.django_db
def test_delete_conversational_pathway(api_client, sample_pathway_data):
    # Create a pathway for deletion
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)

    url = reverse('conversationalpathway-detail', args=[pathway.id])
    
    with patch('agents.views.BlandClient.delete_conversational_pathway') as mock_delete_pathway:
        mock_delete_pathway.return_value = None  # Assume no return value for deletes
        
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify pathway was deleted from the database
        assert ConversationalPathway.objects.filter(id=pathway.id).count() == 0

@pytest.mark.django_db
def test_get_conversational_pathway_list(api_client, sample_pathway_data):
    # Create some pathways
    ConversationalPathway.objects.create(**sample_pathway_data)
    ConversationalPathway.objects.create(name='Another Pathway', description='Another description')
    
    url = reverse('conversationalpathway-list')

    response = api_client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4  # Verify the number of pathways returned

@pytest.mark.django_db
def test_get_single_conversational_pathway(api_client, sample_pathway_data):
    # Create a pathway
    pathway = ConversationalPathway.objects.create(**sample_pathway_data)

    url = reverse('conversationalpathway-detail', args=[pathway.id])

    response = api_client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == pathway.name