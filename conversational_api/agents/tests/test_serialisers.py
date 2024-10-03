import pytest
from agents.serializers import AgentSerializer, ConversationalPathwaySerializer
from agents.models import Agent, ConversationalPathway
from django.core.exceptions import ValidationError as DjangoValidationError
from unittest.mock import patch


# Tests for AgentSerializer

@pytest.mark.django_db
def test_agent_serializer_valid_data():
    data = {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30,
        'keywords': ["test", "agent"]
    }
    serializer = AgentSerializer(data=data)
    assert serializer.is_valid()
    agent = serializer.save()
    
    # Ensure the script was generated correctly from the prompt
    assert agent.script == 'Hello'  # Assuming html_to_script strips HTML tags
    assert agent.keywords == ["test", "agent"]
    assert agent.name == 'Test Agent'

@pytest.mark.django_db
def test_agent_serializer_invalid_prompt():
    data = {
        'name': 'Test Agent',
        'prompt': '   ',  # Invalid prompt (whitespace only)
        'voice': 'default_voice',
        'max_duration': 30
    }
    serializer = AgentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'prompt' in serializer.errors

@pytest.mark.django_db
def test_agent_serializer_invalid_max_duration():
    data = {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': -10  # Invalid max duration (negative value)
    }
    serializer = AgentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'max_duration' in serializer.errors

@pytest.mark.django_db
def test_agent_serializer_update():
    # Create an initial agent
    agent = Agent.objects.create(
        name='Initial Agent',
        prompt='<p>Hello</p>',
        voice='default_voice',
        max_duration=30
    )

    # Update data
    updated_data = {
        'name': 'Updated Agent',
        'prompt': '<p>Updated Hello</p>',
        'voice': 'updated_voice',
        'max_duration': 60
    }

    serializer = AgentSerializer(instance=agent, data=updated_data)
    assert serializer.is_valid()
    updated_agent = serializer.save()

    assert updated_agent.name == 'Updated Agent'
    assert updated_agent.script == 'Updated Hello'  # Assuming HTML is transformed to plain text
    assert updated_agent.voice == 'updated_voice'
    assert updated_agent.max_duration == 60

@pytest.mark.django_db
def test_agent_serializer_create_with_valid_tool():
    data = {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30,
        'tools': [
            {"tool_name": "KnowledgeBase", "description": "Access internal knowledge base."}
        ]  # Valid tool
    }
    serializer = AgentSerializer(data=data)
    
    assert serializer.is_valid()  # The serializer should be valid
    
@pytest.mark.django_db
def test_agent_serializer_create_with_invalid_tool():
    data = {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30,
        'tools': [{"invalid_key": "invalid_value"}]  # Invalid tool object
    }
    serializer = AgentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'tools' in serializer.errors

@pytest.mark.django_db
def test_agent_serializer_empty_keywords():
    data = {
        'name': 'Test Agent',
        'prompt': '<h1>Hello</h1>',
        'voice': 'default_voice',
        'max_duration': 30,
        'keywords': None  # Invalid, should be a list or empty list
    }
    serializer = AgentSerializer(data=data)
    assert not serializer.is_valid()
    assert 'keywords' in serializer.errors


# Tests for ConversationalPathwaySerializer

@pytest.mark.django_db
def test_pathway_serializer_valid_data():
    data = {
        'name': 'Test Pathway',
        'description': 'A test pathway',
        'nodes': {
            "1": {"name": "Start", "text": "Hello"}
        },
        'edges': {
            "1": {"source": "1", "target": "2"}
        }
    }
    serializer = ConversationalPathwaySerializer(data=data)
    assert serializer.is_valid()
    pathway = serializer.save()
    assert pathway.name == 'Test Pathway'
    assert pathway.nodes == {
        "1": {"name": "Start", "text": "Hello"}
    }
    assert pathway.edges == {
        "1": {"source": "1", "target": "2"}
    }

@pytest.mark.django_db
def test_pathway_serializer_invalid_name():
    data = {
        'name': '   ',  # Invalid name (only whitespace)
        'description': 'A test pathway',
        'nodes': {},
        'edges': {}
    }
    serializer = ConversationalPathwaySerializer(data=data)
    assert not serializer.is_valid()
    assert 'name' in serializer.errors

@pytest.mark.django_db
def test_pathway_serializer_update():
    # Create an initial pathway
    pathway = ConversationalPathway.objects.create(
        name='Initial Pathway',
        description='Initial description',
        nodes={"1": {"name": "Start", "text": "Hello"}},
        edges={"1": {"source": "1", "target": "2"}}
    )

    # Update data
    updated_data = {
        'name': 'Updated Pathway',
        'description': 'Updated description',
        'nodes': {
            "1": {"name": "Start", "text": "Updated Hello"}
        },
        'edges': {
            "1": {"source": "1", "target": "2"}
        }
    }

    serializer = ConversationalPathwaySerializer(instance=pathway, data=updated_data)
    assert serializer.is_valid()
    updated_pathway = serializer.save()

    assert updated_pathway.name == 'Updated Pathway'
    assert updated_pathway.description == 'Updated description'
    assert updated_pathway.nodes == {
        "1": {"name": "Start", "text": "Updated Hello"}
    }

@pytest.mark.django_db
def test_pathway_serializer_invalid_nodes():
    data = {
        'name': 'Test Pathway',
        'description': 'A test pathway',
        'nodes': "invalid nodes",  # Invalid nodes (not a dict)
        'edges': {}
    }
    serializer = ConversationalPathwaySerializer(data=data)
    assert not serializer.is_valid()
    assert 'nodes' in serializer.errors

@pytest.mark.django_db
def test_pathway_serializer_invalid_edges():
    data = {
        'name': 'Test Pathway',
        'description': 'A test pathway',
        'nodes': {},
        'edges': "invalid edges"  # Invalid edges (not a dict)
    }
    serializer = ConversationalPathwaySerializer(data=data)
    assert not serializer.is_valid()
    assert 'edges' in serializer.errors