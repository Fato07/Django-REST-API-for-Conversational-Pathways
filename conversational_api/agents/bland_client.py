# agents/bland_client.py
import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .serializers import AgentSerializer
from rest_framework.exceptions import APIException
import json

logger = logging.getLogger(__name__)

class BlandClient:
    def __init__(self):
        self.base_url = 'https://api.bland.ai/v1'
        self.api_key = os.getenv('BLAND_AI_API_KEY')        
        self.session = self._init_session()

    def _init_session(self):
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "OPTIONS", "POST"]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.headers.update({
            'Authorization': f'{self.api_key}',
            'Content-Type': 'application/json',
        })
        return session

    def _prepare_agent_payload(self, agent, request_data):
        """
        Prepares the JSON payload for creating or updating an agent in Bland AI.
        Only includes fields specified in the request data.
        """
        serializer = AgentSerializer(agent)
        data = serializer.data
        
        # Filter out fields that were not in the original request
        cleaned_data = {key: data[key] for key in request_data if key in data}
        
        return cleaned_data

        
    def create_agent(self, agent, request_data):
        """
        Creates an agent in Bland AI using the script as the prompt.
        Returns the `bland_ai_id` of the created agent.
        """
        url = f"{self.base_url}/agents"
        payload = self._prepare_agent_payload(agent, request_data)

        try:
            logger.info(f"Requesting URL: {url}")
            logger.info(f"Request Payload: {json.dumps(payload, indent=4)}")
            
            # Send the request
            response = self.session.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                logger.info(f"Agent Created in Bland Systems successfully")
                 # Log the parsed response
                response_data = response.json()
                logger.info(f"Agent Data: {json.dumps(response_data, indent=4)}")
                
            # Extract and return the `bland_ai_id`
            bland_ai_id = response_data.get('agent', {}).get('agent_id')
            if not bland_ai_id:
                logger.error("Response does not contain 'agent_id'")
                raise APIException("Failed to retrieve bland_ai_id from Bland AI.")
            
            return bland_ai_id
        except requests.exceptions.Timeout:
            logger.error("Request to Bland AI timed out.", exc_info=True)
            raise APIException("Timed out while creating agent in Bland AI.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}", exc_info=True)
            raise APIException("HTTP error occurred while creating agent in Bland AI.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception occurred: {e}", exc_info=True)
            raise APIException("Failed to create agent in Bland AI.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise APIException("An unexpected error occurred while creating agent in Bland AI.")
    
    def update_agent(self, agent, request_data):
        """
        Update an existing agent in Bland AI.
        """
        if not agent.bland_ai_id:
            logger.error("Agent does not have a valid bland_ai_id.")
            raise ValueError("Agent must have a valid bland_ai_id to update.")
        
        url = f"{self.base_url}/agents/{agent.bland_ai_id}"
        payload = self._prepare_agent_payload(agent, request_data)

        try:
            logger.info(f"Updating agent at URL: {url}")
            logger.info(f"Request Payload: {payload}")

            # Make the POST request to Bland AI API with headers and timeout
            response = self.session.post(url, json=payload, timeout=30)
                        
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")
            
            # Raise an error if the response contains an HTTP error status code
            response.raise_for_status()

            # Return the response data as JSON
            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Request to Bland AI timed out.")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}", exc_info=True)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception occurred: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise

    def delete_agent(self, bland_ai_id):
        """
        Delete an agent from Bland AI using the agent's Bland AI ID.
        """
        url = f"{self.base_url}/agents/{bland_ai_id}/delete"
        
        try:
            logger.info(f"Sending delete request to URL: {url}")

            # Make the request to delete the agent from Bland AI
            response = self.session.post(url, timeout=30)

            # Log the response
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()

            # Return the parsed response data
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting agent in Bland AI: {e}", exc_info=True)
            if e.response is not None:
                logger.error(f"Bland AI response status code: {e.response.status_code}")
                logger.error(f"Bland AI response text: {e.response.text}")
    
    def create_conversational_pathway(self, pathway):
        """
        Create a conversational pathway in Bland AI.
        """
        url = f"{self.base_url}/convo_pathway/create"
        payload = {
            "name": pathway.name,
            "description": pathway.description,
        }

        try:
            logger.info(f"Creating conversational pathway at URL: {url}")
            logger.info(f"Request Payload: {payload}")

            # Send the request
            response = self.session.post(url, json=payload, timeout=30)
            
             # Log the response status code and body
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()

            response_data = response.json()
            print(response)
            
            return response_data.get("pathway_id")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating conversational pathway in Bland AI: {e}", exc_info=True)
            raise

    def update_conversational_pathway(self, pathway):
        """
        Update a conversational pathway in Bland AI with the correct structure.
        """
        url = f"{self.base_url}/convo_pathway/{pathway.bland_ai_pathway_id}"

        # Ensure the payload matches the required structure of nodes and edges
        payload = {
            "name": pathway.name,
            "description": pathway.description,
            "nodes": self._format_nodes(pathway.nodes),
            "edges": self._format_edges(pathway.edges)
        }

        try:
            # Log the payload before sending the request for debugging
            logger.info(f"Updating conversational pathway at URL: {url}")
            logger.info(f"Payload: {payload}")

            # Send the update request to Bland AI
            response = self.session.post(url, json=payload, timeout=30)

            # Log the full response body
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            # Log the error with response details for better debugging
            logger.error(f"Error updating conversational pathway in Bland AI: {e}", exc_info=True)
            if e.response is not None:
                logger.error(f"Bland AI response status code: {e.response.status_code}")
                logger.error(f"Bland AI response text: {e.response.text}")
            raise

    def get_conversational_pathway(self, bland_ai_pathway_id):
        """
        Retrieve a conversational pathway from Bland AI.
        """
        url = f"{self.base_url}/convo_pathway/{bland_ai_pathway_id}"

        try:
            logger.info(f"Retrieving conversational pathway from URL: {url}")

            response = self.session.get(url, timeout=30)
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving conversational pathway from Bland AI: {e}", exc_info=True)
            raise
        
    # def get_all_conversational_pathways(self):
    #     """
    #     Retrieve a conversational pathway from Bland AI.
    #     """
    #     url = f"{self.base_url}/convo_pathway"

    #     try:
    #         logger.info(f"Retrieving all conversational pathways from Bland AI at URL: {url}")

    #         response = self.session.get(url, timeout=30)
    #         logger.info(f"Response Status Code: {response.status_code}")
    #         logger.info(f"Response Text: {response.text}")

    #         response.raise_for_status()

    #         return response.json()
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"Error retrieving conversational pathway from Bland AI: {e}", exc_info=True)
    #         raise

    def delete_conversational_pathway(self, bland_ai_pathway_id):
        """
        Delete a conversational pathway in Bland AI.
        """
        url = f"{self.base_url}/convo_pathway/{bland_ai_pathway_id}"
        
        try:
            logger.info(f"Deleting conversational pathway at URL: {url}")

            response = self.session.delete(url, timeout=30)
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting conversational pathway in Bland AI: {e}", exc_info=True)
            raise
    
    def _format_nodes(self, nodes):
        """
        Format the nodes from the local model into the structure Bland AI expects.
        """
        formatted_nodes = []
        for node_id, node_data in nodes.items():
            formatted_node = {
                "id": node_id,
                "data": {
                    "name": node_data.get("name", "Unnamed Node"),
                    "text": node_data.get("text", "")
                },
                "type": node_data.get("type", "Default")
            }
            formatted_nodes.append(formatted_node)
        return formatted_nodes

    def _format_edges(self, edges):
        """
        Format the edges from the local model into the structure Bland AI expects.
        """
        formatted_edges = []
        for edge_id, edge_data in edges.items():
            formatted_edge = {
                "id": edge_id,
                "source": edge_data.get("source", ""),
                "target": edge_data.get("target", ""),
                "data": {
                    "name": edge_data.get("name", "Unnamed Edge"),
                    "prompt": edge_data.get("prompt", "")
                }
            }
            formatted_edges.append(formatted_edge)
        return formatted_edges