# agents/bland_client.py

import requests
import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

    def create_agent(self, agent):
        """
        Create an agent in Bland AI using the script as the prompt.
        """
        url = f"{self.base_url}/agents"
        payload = self._prepare_agent_payload(agent)

        try:
            logger.info(f"Requesting URL: {url}")
            logger.info(f"Request Payload: {payload}")
            
            # Send the request
            response = self.session.post(url, json=payload, timeout=60)

            # Log the response status code and body
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()

            # Log the parsed response
            response_data = response.json()
            logger.info(f"Parsed Response: {response_data}")

            return response_data.get('agent', {}).get('agent_id')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating agent in Bland AI: {e}", exc_info=True)
            if e.response is not None:
                logger.error(f"Bland AI response status code: {e.response.status_code}")
                logger.error(f"Bland AI response text: {e.response.text}")
            raise

    def update_agent(self, agent):
        url = f"{self.base_url}/agents/{agent.bland_ai_id}" 
        payload = self._prepare_agent_payload(agent)

        try:
            logger.info(f"Updating agent at URL: {url}")
            logger.info(f"Request Payload: {payload}")

            # Make the POST request to Bland AI API with headers and timeout
            response = self.session.post(url, json=payload, timeout=30)
                        
            # Log the response status and body correctly
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
            logger.error(f"Error updating agent in Bland AI: {e}", exc_info=True)
            if e.response is not None:
                logger.error(f"Bland AI response status code: {e.response.status_code}")
                logger.error(f"Bland AI response text: {e.response.text}")
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
        

    def _prepare_agent_payload(self, agent):
        payload = {
            "prompt": agent.script, # Use the script (plain text) as the prompt
            "voice": agent.voice,
            "language": agent.language,
            "model": agent.model,
            # Add other fields as required
        }
        return payload