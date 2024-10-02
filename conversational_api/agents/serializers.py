from rest_framework import serializers
from .models import Agent, ConversationalPathway
from .utils import html_to_script
import logging

logger = logging.getLogger(__name__)

class AgentSerializer(serializers.ModelSerializer):
    script = serializers.SerializerMethodField(read_only=True)  # Script becomes the prompt
    
    prompt = serializers.CharField(required=True)  # Only prompt is required
    name = serializers.CharField(required=False)  # Optional fields
    voice = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    model = serializers.CharField(required=False)

    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'prompt', 'script', 'voice', 'language',
            'model', 'bland_ai_id', 'version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'script', 'bland_ai_id', 'version', 'created_at', 'updated_at']

    def get_script(self, obj):
        """
        Converts html_input to a standardized script format (which acts as the prompt).
        """
        return html_to_script(obj.prompt)

    def create(self, validated_data):
        """
        Creates a new Agent instance, converts HTML to plain text for prompt, and handles Bland AI synchronization.
        """
        # Convert HTML input to script (plain text prompt)
        script = html_to_script(validated_data['prompt'])
        validated_data['script'] = script
        
        # Create the agent in the local database
        agent = Agent.objects.create(**validated_data)
        return agent

    def update(self, instance, validated_data):
        """
        Updates an existing Agent instance.
        """
        # Update the agent and re-convert the HTML input to plain text prompt
        instance.prompt = validated_data.get('prompt', instance.prompt)  # Prompt is required and updated
        instance.name = validated_data.get('name', instance.name)  # Optional fields
        instance.voice = validated_data.get('voice', instance.voice)
        instance.language = validated_data.get('language', instance.language)
        instance.model = validated_data.get('model', instance.model)

        instance.version += 1  # Increment version

        # Convert HTML input to script (plain text prompt)
        instance.script = html_to_script(instance.prompt)  # Convert prompt to script
        instance.save()
        return instance
    
class ConversationalPathwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationalPathway
        fields = [
            'id', 'name', 'description', 'bland_ai_pathway_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'bland_ai_pathway_id', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """
        Creates a new ConversationalPathway instance.
        """
        pathway = ConversationalPathway.objects.create(**validated_data)
        return pathway

    def update(self, instance, validated_data):
        """
        Updates an existing ConversationalPathway instance.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance