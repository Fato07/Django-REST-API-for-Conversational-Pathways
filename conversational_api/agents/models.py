from rest_framework import serializers
from .models import Agent, ConversationalPathway
from .utils import html_to_script
from django.db import transaction
from django.core.exceptions import ValidationError

class AgentSerializer(serializers.ModelSerializer):
    script = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = ['id', 'bland_ai_id', 'script', 'version', 'created_at', 'updated_at']

    def get_script(self, obj):
        """
        Converts HTML input to a script using a utility function.

        Args:
            obj (Agent): The agent instance.

        Returns:
            str: The generated script or None if no HTML input exists.
        """
        if obj.html_input:
            return html_to_script(obj.html_input)
        return None

    def create(self, validated_data):
        """
        Creates an agent instance and synchronizes it with Bland AI.

        Args:
            validated_data (dict): The validated data for agent creation.

        Returns:
            Agent: The created Agent instance.
        """
        with transaction.atomic():
            agent = Agent.objects.create(**validated_data)
            agent.script = self.get_script(agent)
            agent.save()

            # Synchronize with Bland AI
            from .bland_client import BlandClient
            client = BlandClient()
            try:
                bland_agent_id = client.create_agent(agent)
            except Exception as e:
                raise serializers.ValidationError({"bland_ai": f"Failed to synchronize with Bland AI: {str(e)}"})
            agent.bland_ai_id = bland_agent_id
            agent.save()

            return agent

    def update(self, instance, validated_data):
        """
        Updates an agent instance and synchronizes it with Bland AI.

        Args:
            instance (Agent): The existing agent instance.
            validated_data (dict): The validated data for updating the agent.

        Returns:
            Agent: The updated agent instance.
        """
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.script = self.get_script(instance)
            instance.save()

            # Synchronize with Bland AI
            from .bland_client import BlandClient
            client = BlandClient()
            try:
                client.update_agent(instance)
            except Exception as e:
                raise serializers.ValidationError({"bland_ai": f"Failed to synchronize with Bland AI: {str(e)}"})

            return instance

class ConversationalPathwaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationalPathway
        fields = '__all__'
        read_only_fields = ['id', 'bland_ai_pathway_id', 'created_at']

    def create(self, validated_data):
        """
        Creates a conversational pathway and synchronizes it with Bland AI.

        Args:
            validated_data (dict): The validated data for pathway creation.

        Returns:
            ConversationalPathway: The created pathway instance.
        """
        with transaction.atomic():
            pathway = ConversationalPathway.objects.create(**validated_data)

            # Synchronize with Bland AI
            from .bland_client import BlandClient
            client = BlandClient()
            agent_bland_id = pathway.agent.bland_ai_id
            try:
                bland_pathway_id = client.create_pathway(agent_bland_id, pathway)
            except Exception as e:
                raise serializers.ValidationError({"bland_ai": f"Failed to synchronize pathway with Bland AI: {str(e)}"})
            pathway.bland_ai_pathway_id = bland_pathway_id
            pathway.save()

            return pathway
