#!/usr/bin/env python3
"""
NETVEXA API Python Example
Demonstrates common API operations
"""

import os
import requests
import time
from typing import Dict, Any

class NetvexaClient:
    def __init__(self, api_key: str, base_url: str = "https://api.netvexa.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def create_agent(self, name: str, description: str, **kwargs) -> Dict[str, Any]:
        """Create a new agent"""
        data = {
            "name": name,
            "description": description,
            "model": kwargs.get("model", "gpt-3.5-turbo"),
            "welcome_message": kwargs.get("welcome_message", "Hello! How can I help you today?"),
            "collect_email": kwargs.get("collect_email", True)
        }
        return self._request("POST", "/agents", json=data)
    
    def upload_document(self, agent_id: str, file_path: str, title: str = None) -> Dict[str, Any]:
        """Upload a document to agent's knowledge base"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'agent_id': agent_id}
            if title:
                data['title'] = title
            
            # Use multipart/form-data for file upload
            headers = {"X-API-Key": self.api_key}
            response = requests.post(
                f"{self.base_url}/knowledge/ingest/file",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    def test_agent(self, agent_id: str, message: str) -> Dict[str, Any]:
        """Test agent with a message"""
        return self._request("POST", f"/agents/{agent_id}/test-message", params={"message": message})
    
    def deploy_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deploy agent and get embed code"""
        return self._request("POST", f"/agents/{agent_id}/deploy")
    
    def get_analytics(self, agent_id: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get agent analytics"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._request("GET", f"/agents/{agent_id}/analytics", params=params)
    
    def list_conversations(self, agent_id: str, status: str = None) -> Dict[str, Any]:
        """List agent conversations"""
        params = {}
        if status:
            params['status'] = status
        return self._request("GET", f"/agents/{agent_id}/conversations", params=params)

def main():
    # Initialize client
    api_key = os.getenv("NETVEXA_API_KEY")
    if not api_key:
        print("Please set NETVEXA_API_KEY environment variable")
        return
    
    client = NetvexaClient(api_key)
    
    try:
        # 1. Create an agent
        print("Creating agent...")
        agent = client.create_agent(
            name="Product Support Bot",
            description="Helps customers with product questions and troubleshooting",
            model="gpt-3.5-turbo",
            welcome_message="Hi! I'm here to help with any product questions. What can I assist you with today?"
        )
        agent_id = agent['id']
        print(f"✓ Agent created: {agent_id}")
        
        # 2. Upload knowledge base documents
        print("\nUploading knowledge base...")
        # Example: Upload a product manual
        # document = client.upload_document(
        #     agent_id=agent_id,
        #     file_path="product_manual.pdf",
        #     title="Product Manual v2.0"
        # )
        # print(f"✓ Document uploaded: {document['id']}")
        
        # 3. Test the agent
        print("\nTesting agent...")
        test_response = client.test_agent(
            agent_id=agent_id,
            message="What are your business hours?"
        )
        print(f"✓ Test response: {test_response['response']}")
        
        # 4. Deploy the agent
        print("\nDeploying agent...")
        deployment = client.deploy_agent(agent_id)
        print(f"✓ Agent deployed!")
        print(f"Embed code:\n{deployment['embed_code']}")
        
        # 5. Get analytics (after some usage)
        print("\nFetching analytics...")
        analytics = client.get_analytics(agent_id)
        print(f"✓ Total conversations: {analytics['metrics']['total_conversations']}")
        print(f"✓ Unique visitors: {analytics['metrics']['unique_visitors']}")
        
        # 6. List recent conversations
        print("\nListing conversations...")
        conversations = client.list_conversations(agent_id, status="active")
        print(f"✓ Active conversations: {conversations['total']}")
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e.response, 'json'):
            print(f"Details: {e.response.json()}")

if __name__ == "__main__":
    main()