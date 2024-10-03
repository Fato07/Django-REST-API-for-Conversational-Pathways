#agents/serialisers.py
from rest_framework import serializers
from .models import Agent, ConversationalPathway
from .utils import html_to_script
import logging
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)

class AgentSerializer(serializers.ModelSerializer):
    
    name = serializers.CharField(required=True, allow_blank=False)
    bland_ai_id = serializers.CharField(read_only=True) # Exclude bland_ai_id from writable fields since it's managed by the system
    prompt = serializers.CharField(required=True, allow_blank=False)
    script = serializers.SerializerMethodField(read_only=True)  # Script becomes the prompt
    voice = serializers.CharField(required=False, allow_blank=True)
    analysis_schema = serializers.JSONField(required=False, default=dict)
    metadata = serializers.JSONField(required=False, default=dict)
    pathway_id = serializers.CharField(required=False, allow_blank=True, default="")
    language = serializers.CharField(required=False, allow_blank=True)
    model = serializers.CharField(required=False, allow_blank=True)
    first_sentence = serializers.CharField(required=False, allow_blank=True, default="")
    tools = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()), 
        required=False, 
        default=list
    )
    dynamic_data = serializers.JSONField(required=False, default=dict)
    interruption_threshold = serializers.IntegerField(required=False, default=100)
    keywords = serializers.JSONField(required=False, allow_null=True, default=dict)
    max_duration = serializers.IntegerField(required=False, default=30)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    version = serializers.IntegerField(read_only=True)
    webhook = serializers.URLField(required=False, allow_null=True, allow_blank=True, default=None)  # Changed default to None


    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'bland_ai_id', 'prompt', 'script', 'voice',
            'analysis_schema','metadata', 'pathway_id', 'language',
            'model', 'first_sentence', 'tools', 'dynamic_data', 'interruption_threshold','keywords',
            'max_duration', 'created_at', 'updated_at' ,'version', 'webhook'
        ]
        read_only_fields = [
            'id', 'script', 'bland_ai_id', 'version', 
            'created_at', 'updated_at'
        ]
    
    def get_script(self, obj):
        return html_to_script(obj.prompt)
    
    def validate_prompt(self, value):
        """
        Ensure that the prompt is not empty or only whitespace.
        """
        if not value.strip():
            raise serializers.ValidationError("Prompt cannot be empty or blank.")
        return value
    
    def validate_model(self, value):
        allowed_models = ["base", "turbo", "enhanced"]
        if value and value not in allowed_models:
            raise serializers.ValidationError(f"Model must be one of {allowed_models}.")
        return value

    def validate_keywords(self, value):
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("Keywords must be a list of strings.")
            for keyword in value:
                if not isinstance(keyword, str) or not keyword.strip():
                    raise serializers.ValidationError("Each keyword must be a non-empty string.")
        return value

    def validate_max_duration(self, value):
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise serializers.ValidationError("Max duration must be a positive integer.")
        return value

    def validate_tools(self, value):
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("Tools must be a list of objects.")
            for tool in value:
                if not isinstance(tool, dict) or not tool:
                    raise serializers.ValidationError("Each tool must be a non-empty object with valid configurations.")
        return value
    
    def create(self, validated_data):
        """
        Creates a new Agent instance, converts HTML to plain text for prompt.
        Note: `bland_ai_id` is assigned after successful creation in Bland AI.
        """
        # Convert HTML input to script (plain text prompt)
        try:
            validated_data['script'] = html_to_script(validated_data['prompt'])
            agent = Agent(**validated_data)
            agent.full_clean()  # Perform model validation
            agent.save()
            return agent
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

    def update(self, instance, validated_data):
        """
        Updates an existing Agent instance.
        """
        # Update the agent's fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.script = html_to_script(instance.prompt)
        instance.version += 1
        
        try:
            instance.full_clean()  # Perform model validation
            instance.save()
            return instance
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
    
class ConversationalPathwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationalPathway
        fields = [
            'id', 'name', 'description', 'bland_ai_pathway_id',
            'nodes', 'edges', 'created_at', 'updated_at'
        ]
        
        read_only_fields = ['id', 'bland_ai_pathway_id', 'created_at', 'updated_at']

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
        instance.nodes = validated_data.get('nodes', instance.nodes)
        instance.edges = validated_data.get('edges', instance.edges)
        
        instance.version += 1  # Increment version

        instance.save()
        
        print(instance)
        return instance