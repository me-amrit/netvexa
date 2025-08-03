#!/usr/bin/env python3
"""
Test script to verify safe agent deletion functionality
"""
import asyncio
import requests
import json

BASE_URL = "http://localhost:8000"

async def test_agent_deletion():
    """Test the agent deletion functionality"""
    
    # 1. Try to register a test user first
    print("👤 Registering test user...")
    register_data = {
        "email": "test@netvexa.com",
        "password": "test123",
        "company_name": "Test Company"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    if response.status_code == 201:
        print("✅ Test user registered successfully")
    elif response.status_code == 400 and "already registered" in response.text:
        print("ℹ️ Test user already exists")
    else:
        print(f"❌ Registration failed: {response.text}")
        
    # 2. Login to get auth token
    print("🔐 Logging in...")
    login_data = {
        "username": "test@netvexa.com",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # 3. Get list of agents
    print("\n📋 Fetching agents list...")
    response = requests.get(f"{BASE_URL}/api/agents", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch agents: {response.text}")
        return
    
    agents = response.json()
    if not agents:
        print("ℹ️ No agents found to test deletion")
        return
    
    agent = agents[0]  # Use the first agent for testing
    print(f"✅ Found agent: {agent['name']} (ID: {agent['id']})")
    print(f"   - Conversations: {agent.get('conversation_count', 0)}")
    print(f"   - Documents: {agent.get('document_count', 0)}")
    
    # 3. Get detailed agent info before deletion
    print(f"\n🔍 Getting detailed info for agent {agent['id']}...")
    response = requests.get(f"{BASE_URL}/api/agents/{agent['id']}", headers=headers)
    if response.status_code == 200:
        detailed_agent = response.json()
        print(f"✅ Agent details retrieved")
        print(f"   - Name: {detailed_agent['name']}")
        print(f"   - Conversations: {detailed_agent.get('conversation_count', 0)}")
        print(f"   - Documents: {detailed_agent.get('document_count', 0)}")
    
    # 4. Get conversations for this agent
    print(f"\n💬 Getting conversations for agent {agent['id']}...")
    response = requests.get(f"{BASE_URL}/api/agents/{agent['id']}/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
        for conv in conversations[:3]:  # Show first 3
            print(f"   - Conversation {conv['id']}: {conv.get('message_count', 0)} messages")
    
    # 5. Get documents for this agent  
    print(f"\n📄 Getting documents for agent {agent['id']}...")
    response = requests.get(f"{BASE_URL}/api/agents/{agent['id']}/documents", headers=headers)
    if response.status_code == 200:
        documents = response.json()
        print(f"✅ Found {len(documents)} documents")
        for doc in documents[:3]:  # Show first 3
            print(f"   - Document {doc['id']}: {doc['name']}")
    
    # 6. Ask user for confirmation before actual deletion
    print(f"\n⚠️  About to test deletion of agent: {agent['name']}")
    print("   This will permanently delete:")
    print(f"   - The agent and its configuration")
    print(f"   - {agent.get('conversation_count', 0)} conversations and all messages")
    print(f"   - {agent.get('document_count', 0)} knowledge documents")
    print("   - All analytics and history data")
    
    confirm = input("\n❓ Do you want to proceed with deletion? (type 'yes' to confirm): ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled")
        return
    
    # 7. Perform the deletion
    print(f"\n🗑️ Deleting agent {agent['id']}...")
    response = requests.delete(f"{BASE_URL}/api/agents/{agent['id']}", headers=headers)
    
    if response.status_code == 200:
        print("✅ Agent deleted successfully!")
        result = response.json()
        print(f"   Message: {result.get('message', 'No message')}")
    else:
        print(f"❌ Deletion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # 8. Verify deletion by trying to fetch the agent
    print(f"\n🔍 Verifying deletion...")
    response = requests.get(f"{BASE_URL}/api/agents/{agent['id']}", headers=headers)
    if response.status_code == 404:
        print("✅ Agent successfully deleted - returns 404 as expected")
    else:
        print(f"❌ Agent still exists - unexpected status: {response.status_code}")
    
    # 9. Check if conversations are also deleted
    print(f"\n💬 Checking if conversations were deleted...")
    response = requests.get(f"{BASE_URL}/api/agents/{agent['id']}/conversations", headers=headers)
    if response.status_code == 404:
        print("✅ Conversations endpoint returns 404 as expected")
    else:
        print(f"❓ Conversations endpoint status: {response.status_code}")
    
    print(f"\n🎉 Agent deletion test completed!")

if __name__ == "__main__":
    asyncio.run(test_agent_deletion())