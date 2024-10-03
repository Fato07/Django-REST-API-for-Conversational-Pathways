#agents/views.py
from requests import Response

from .utils import html_to_script
from .serializers import AgentSerializer, ConversationalPathwaySerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Agent, ConversationalPathway
from .bland_client import BlandClient
import logging
from django.db import transaction
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

class AgentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Agent instances.
    """
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [AllowAny]
            
    def get_script(self, obj):
        return html_to_script(obj.prompt)
    
    def perform_create(self, serializer):
        """
        Creates an Agent instance and synchronizes it with Bland AI.
        Ensures that `bland_ai_id` is always set.
        """
        client = BlandClient()
        try:
            with transaction.atomic():
                # Save the agent locally without `bland_ai_id`
                agent = serializer.save()
                logger.info(f"Agent '{agent.name}' created locally with ID {agent.id}.")
                                
                # Create the agent in Bland AI
                bland_ai_id = client.create_agent(agent, self.request.data)
    
                # Update the agent with `bland_ai_id`
                agent.bland_ai_id = bland_ai_id
                agent.save()
                logger.info(f"Agent '{agent.name}' synchronized with Bland AI, bland_ai_id: {bland_ai_id}.")
                
        except APIException as e:
            logger.error(f"APIException during agent creation: {e}", exc_info=True)
            agent.delete()
            raise 
    
    def perform_update(self, serializer):
        """
        Updates an Agent instance and synchronizes the changes with Bland AI.
        """
        client = BlandClient()
        try:
            with transaction.atomic():
                agent = serializer.save()
                logger.info(f"Agent '{agent.name}' updated locally with ID {agent.id}.")

                # Ensure `bland_ai_id` is present
                if not agent.bland_ai_id:
                    logger.error("Agent does not have a valid bland_ai_id.")
                    raise APIException("Agent lacks a valid Bland AI ID.")

                # Update the agent in Bland AI
                client.update_agent(agent, self.request.data)
                logger.info(f"Agent '{agent.name}' synchronized with Bland AI.")

        except Exception as e:
            logger.error(f"Error during agent update or synchronization: {e}", exc_info=True)
            raise APIException("Failed to update agent and synchronize with Bland AI.")

    def perform_destroy(self, instance):
        """
        Deletes an Agent instance locally and from Bland AI.
        """
        client = BlandClient()

        try:
            with transaction.atomic():
                # Attempt to delete from Bland AI
                if instance.bland_ai_id:
                    client.delete_agent(instance.bland_ai_id)
                    logger.info(f'Agent "{instance.name}" successfully deleted from Bland AI.')
                else:
                    logger.warning(f'Agent "{instance.name}" has no bland_ai_id. Skipping Bland AI deletion.')

                # Now delete the agent from the local database
                instance.delete()
                logger.info(f'Agent with name "{instance.name}" successfully deleted locally.')
        except APIException as e:
            logger.error(f"APIException during agent deletion: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during agent deletion: {e}", exc_info=True)
            raise APIException("Failed to delete agent from Bland AI and locally.")
   

class ConversationalPathwayViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing ConversationalPathway instances.
    """
    queryset = ConversationalPathway.objects.all().order_by('created_at')
    serializer_class = ConversationalPathwaySerializer
    permission_classes = [AllowAny]

    # def list(self, request, *args, **kwargs):
    #     """
    #     Override the list method to fetch data from Bland AI and synchronize with the local database.
    #     """
    #     client = BlandClient()

    #     try:
    #         # Fetch the pathways from Bland AI
    #         bland_ai_pathways = client.get_all_conversational_pathways()

    #         # Sync Bland AI pathways with the local database
    #         for pathway_data in bland_ai_pathways:
    #             # Sync fields from Bland AI to the local database
    #             pathway, created = ConversationalPathway.objects.update_or_create(
    #                 bland_ai_pathway_id=pathway_data['id'],
    #                 defaults={
    #                     'name': pathway_data.get('name', ''),
    #                     'description': pathway_data.get('description', ''),
    #                     'nodes': pathway_data.get('nodes', {}),
    #                     'edges': pathway_data.get('edges', {}),
    #                 }
    #             )

    #         # After synchronization, return the local pathways
    #         queryset = self.get_queryset()
    #         serializer = self.get_serializer(queryset, many=True)
    #         return Response(serializer.data)

    #     except Exception as e:
    #         logger.error(f"Error retrieving pathways from Bland AI: {e}")
    #         return Response(
    #             {"detail": "Error retrieving pathways from Bland AI."},
    #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

    # def retrieve(self, request, *args, **kwargs):
    #     """
    #     Override the retrieve method to fetch data from Bland AI and merge it with local data.
    #     """
    #     instance = self.get_object()
    #     client = BlandClient()

    #     try:
    #         # Fetch pathway details from Bland AI
    #         bland_ai_pathway_data = client.get_conversational_pathway(instance.bland_ai_pathway_id)
    #         logger.info(f"Successfully retrieved pathway from Bland AI: {bland_ai_pathway_data}")

    #         # Combine local data with Bland AI data
    #         pathway_data = {
    #             "id": instance.id,
    #             "name": bland_ai_pathway_data.get("name", instance.name),
    #             "description": bland_ai_pathway_data.get("description", instance.description),
    #             "nodes": bland_ai_pathway_data.get("nodes", []),  
    #             "edges": bland_ai_pathway_data.get("edges", []),
    #             "bland_ai_pathway_id": instance.bland_ai_pathway_id,
    #             "created_at": instance.created_at,
    #             "updated_at": instance.updated_at
    #         }

    #         # Return the combined data
    #         return Response(pathway_data)

    #     except Exception as e:
    #         logger.error(f"Error retrieving pathway from Bland AI: {e}")
    #         return Response({"detail": "Error retrieving pathway from Bland AI."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def perform_create(self, serializer):
        """
        Called when saving a new ConversationalPathway instance. Synchronizes with Bland AI.
        """
        client = BlandClient()
        try:
            with transaction.atomic():
                #save the pathway locally
                pathway = serializer.save()
                logger.info(f"Conversational Pathway '{pathway.name}' created locally with ID {pathway.id}.")

                # Create the pathway in Bland AI
                bland_ai_pathway_id = client.create_conversational_pathway(pathway, self.request.data)
                
                pathway.bland_ai_pathway_id = bland_ai_pathway_id
                pathway.save()
                logger.info(f"Conversational Pathway '{pathway.name}' synchronized with Bland AI, bland_ai_pathway_id: {bland_ai_pathway_id}.")
                
                # Serialize the pathway instance to JSON format
                response_data = {
                    'message': 'Conversational Pathway created successfully!',
                    'id': pathway.id,
                    'name': pathway.name,
                    'description': pathway.description,
                    'bland_ai_pathway_id': bland_ai_pathway_id,
                    'nodes': pathway.nodes,
                    'edges': pathway.edges,
                    'created_at': pathway.created_at,
                    'updated_at': pathway.updated_at,
                    }

                return Response(response_data, status=status.HTTP_201_CREATED)
        except APIException as e:
            logger.error(f"APIException during pathway creation: {e}", exc_info=True)
            pathway.delete()
            return Response({"detail": "Error occurred while creating the pathway."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def perform_update(self, serializer):
        """
        Updates a Pathway instance and synchronizes the changes with Bland AI.
        """
        client = BlandClient()
        try:
            with transaction.atomic():
                pathway = serializer.save()
                logger.info(f"Conversational Pathway '{pathway.name}' updated locally with ID {pathway.id}.")

                # Ensure `bland_ai_id` is present
                if not pathway.bland_ai_pathway_id:
                    logger.error("Conversational Pathway does not have a valid bland_ai_pathway_id.")
                    raise APIException("Conversational Pathway lacks a valid Bland AI Pathway ID.")

                # Update the agent in Bland AI
                client.update_conversational_pathway(pathway, self.request.data)
                logger.info(f"Agent '{pathway.name}' synchronized with Bland AI.")
                return Response(status=status.HTTP_200_OK)
        except APIException as e:
            logger.error(f"APIException during pathway update: {e}", exc_info=True)
            return Response({"detail": "Error occurred while updating the pathway."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_destroy(self, instance):
        """
        Called when deleting a ConversationalPathway instance. Synchronizes deletion with Bland AI.
        """
        client = BlandClient()
        try:
            with transaction.atomic():
                # Attempt to delete from Bland AI
                if instance.bland_ai_pathway_id:
                    client.delete_conversational_pathway(instance.bland_ai_pathway_id)
                    logger.info(f'Agent "{instance.name}" successfully deleted from Bland AI.')
                else:
                    logger.warning(f'Agent "{instance.name}" has no bland_ai_pathway_id. Skipping Bland AI deletion.')

                # Now delete the agent from the local database
                instance.delete()
                logger.info(f'Conveersational Pathway with name: "{instance.name}" successfully deleted locally.')
                # Return a success response to the user
                return Response(
                    {
                        "message": "Conversational Pathway deleted successfully!",
                        "id": instance.id,
                        "name": instance.name,
                        "bland_ai_pathway_id": instance.bland_ai_pathway_id
                    },
                    status=status.HTTP_200_OK
                )
        except APIException as e:
            logger.error(f"APIException during pathway deletion: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during pathway deletion: {e}", exc_info=True)
            return Response(
            {
                "message": "Failed to delete the pathway.",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)