import pytest
from agents.models import Agent, ConversationalPathway
from django.core.exceptions import ValidationError

# Test cases for Agent model
@pytest.mark.django_db
def test_agent_creation():
    agent = Agent(
        name='Test Agent',
        prompt='<h1>Hello</h1>',
        voice='default_voice',
        max_duration=30
    )
    agent.save()
    assert agent.id is not None
    assert agent.version == 0
    assert agent.script == 'Hello'  # Assuming html_to_script removes HTML tags
    assert agent.voice == 'default_voice'
    assert agent.max_duration == 30

@pytest.mark.django_db
def test_agent_default_values():
    agent = Agent(
        name='Default Agent',
        prompt='<p>Hello Default</p>'
    )
    agent.save()
    
    # Assert default values
    assert agent.voice == 'default_voice'
    assert agent.max_duration == 30  # Check if default duration was assigned
    assert agent.language == 'ENG'  # Assuming default language is 'ENG'

def test_agent_invalid_prompt():
    agent = Agent(
        name='Test Agent',
        prompt='   ',  # Invalid prompt (only whitespace)
        voice='default_voice',
        max_duration=30
    )
    with pytest.raises(ValidationError):
        agent.full_clean()

@pytest.mark.django_db
def test_agent_invalid_max_duration():
    agent = Agent(
        name='Test Agent',
        prompt='<h1>Hello</h1>',
        voice='default_voice',
        max_duration=-10  # Invalid max duration
    )
    with pytest.raises(ValidationError):
        agent.full_clean()

@pytest.mark.django_db
def test_agent_version_increment_on_update():
    agent = Agent.objects.create(name='Test Agent', prompt='<p>Hello</p>', voice='default_voice', max_duration=30)
    
    initial_version = agent.version
    agent.prompt = '<p>Updated Hello</p>'  # Update a field
    agent.save()

    agent.refresh_from_db()
    assert agent.version == initial_version + 1  # Ensure version is incremented

@pytest.mark.django_db
def test_agent_model_validation():
    agent = Agent(
        name='',  # Invalid name
        prompt='Test Prompt',
        max_duration=0  # Invalid duration
    )
    with pytest.raises(ValidationError):
        agent.full_clean()  # Ensure validation catches the issues

@pytest.mark.django_db
def test_agent_model_save():
    agent = Agent(
        name='Test Agent',
        prompt='Hello',
        max_duration=60
    )
    agent.save()
    assert agent.id is not None  # Ensure the agent was saved to the database


# Test cases for ConversationalPathway model

@pytest.mark.django_db
def test_pathway_creation():
    pathway = ConversationalPathway(
        name='Test Pathway',
        description='A test pathway',
        nodes={
            "id": "randomnode_Test",
            "type": "Default",
            "data": {
                "name": "Test Node",
                "text": "Select a node or edge and press backspace to remove it",
                "globalPrompt": "This is a phone call. Do not use exclamation marks.\n\nConvert 24HR format timings to 12 HR format - e.g 14:00 should be written as 2 PM."
                }},
        edges={
            "id": "randomedge_Test",
            "source": "Test",
            "target": "test",
            "label": "test"
        }
    )
    pathway.save()
    assert pathway.id is not None
    assert pathway.version == 0
    assert pathway.name == 'Test Pathway'

@pytest.mark.django_db
def test_pathway_default_values():
    pathway = ConversationalPathway(
        name='Default Pathway',
        description='A pathway without nodes and edges'
    )
    pathway.save()
    
    assert pathway.nodes == {}  # Should have default value for nodes (empty dict)
    assert pathway.edges == {}  # Should have default value for edges (empty dict)
    assert pathway.version == 0  # Default version

@pytest.mark.django_db
def test_pathway_version_increment_on_update():
    pathway = ConversationalPathway.objects.create(
        name='Test Pathway',
        description='Initial description',
        nodes={"1": {"name": "Start", "text": "Hello"}},
        edges={"1": {"source": "1", "target": "2"}}
    )
    
    initial_version = pathway.version
    pathway.description = 'Updated description'
    pathway.save()

    pathway.refresh_from_db()
    assert pathway.version == initial_version + 1  # Version should increment after an update

def test_pathway_invalid_name():
    pathway = ConversationalPathway(
        name='   ',  # Invalid name (only whitespace)
        description='A test pathway'
    )
    with pytest.raises(ValidationError):
        pathway.full_clean()

@pytest.mark.django_db
def test_pathway_invalid_nodes_format():
    pathway = ConversationalPathway(
        name='Test Pathway',
        description='A test pathway',
        nodes="Invalid Node Data",  # Invalid nodes (should be a dict)
        edges={}
    )
    with pytest.raises(ValidationError):
        pathway.full_clean()

@pytest.mark.django_db
def test_pathway_invalid_edges_format():
    pathway = ConversationalPathway(
        name='Test Pathway',
        description='A test pathway',
        nodes={},
        edges="Invalid Edges Data"  # Invalid edges (should be a dict)
    )
    with pytest.raises(ValidationError):
        pathway.full_clean()

@pytest.mark.django_db
def test_pathway_model_save():
    pathway = ConversationalPathway(
        name='Test Pathway',
        description='A pathway for testing',
        nodes={
            "1": {"name": "Start", "text": "Hello"}
        },
        edges={
            "1": {"source": "1", "target": "2"}
        }
    )
    pathway.save()
    assert pathway.id is not None  # Ensure the pathway was saved to the database