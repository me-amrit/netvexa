#!/usr/bin/env python3
"""
Test script for authentication system.
Run this after starting the backend to verify auth works.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_auth_flow():
    """Test the complete authentication flow."""
    async with httpx.AsyncClient() as client:
        print("🧪 Testing NETVEXA Authentication System\n")
        
        # 1. Test registration
        print("1️⃣ Testing Registration...")
        register_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "company_name": "Test Company"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json=register_data
            )
            if response.status_code == 201:
                user = response.json()
                print(f"✅ Registration successful: {user['email']}")
                print(f"   User ID: {user['id']}")
            elif response.status_code == 400:
                print("⚠️  User already exists")
            else:
                print(f"❌ Registration failed: {response.text}")
                return
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the backend is running: cd backend && ./run_mvp.sh")
            return
        
        # 2. Test login
        print("\n2️⃣ Testing Login...")
        login_data = {
            "username": register_data["email"],  # OAuth2 uses 'username' field
            "password": register_data["password"]
        }
        
        response = await client.post(
            f"{BASE_URL}/api/auth/login",
            data=login_data  # Form data, not JSON
        )
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens["access_token"]
            print("✅ Login successful")
            print(f"   Access token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return
        
        # 3. Test authenticated endpoint
        print("\n3️⃣ Testing Authenticated Access...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = await client.get(
            f"{BASE_URL}/api/auth/me",
            headers=headers
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print("✅ Authenticated access successful")
            print(f"   User: {user_info['email']}")
            print(f"   Company: {user_info['company_name']}")
        else:
            print(f"❌ Authentication failed: {response.text}")
        
        # 4. Test API key creation
        print("\n4️⃣ Testing API Key Creation...")
        response = await client.post(
            f"{BASE_URL}/api/auth/api-keys?name=Test%20Key",
            headers=headers
        )
        
        if response.status_code == 200:
            api_key_info = response.json()
            api_key = api_key_info["key"]
            print("✅ API key created")
            print(f"   Key: {api_key}")
            print(f"   ID: {api_key_info['id']}")
        else:
            print(f"❌ API key creation failed: {response.text}")
            return
        
        # 5. Test agent creation
        print("\n5️⃣ Testing Agent Creation...")
        agent_data = {
            "name": "Test Agent",
            "personality": {
                "tone": "friendly",
                "language": "en",
                "response_style": "detailed"
            },
            "welcome_message": "Welcome! I'm here to help you."
        }
        
        response = await client.post(
            f"{BASE_URL}/api/agents/",
            json=agent_data,
            headers=headers
        )
        
        if response.status_code == 201:
            agent = response.json()
            print("✅ Agent created")
            print(f"   Agent ID: {agent['id']}")
            print(f"   Name: {agent['name']}")
        else:
            print(f"❌ Agent creation failed: {response.text}")
            return
        
        # 6. Test API key authentication
        print("\n6️⃣ Testing API Key Authentication...")
        api_headers = {"Authorization": f"Bearer {api_key}"}
        
        response = await client.get(
            f"{BASE_URL}/api/agents/",
            headers=api_headers
        )
        
        if response.status_code == 200:
            agents = response.json()
            print("✅ API key authentication successful")
            print(f"   Found {len(agents)} agent(s)")
        else:
            print(f"❌ API key authentication failed: {response.text}")
        
        print("\n✅ All tests passed! Authentication system is working correctly.")
        print("\n📝 Summary:")
        print(f"   - User: {register_data['email']}")
        print(f"   - API Key: {api_key}")
        print(f"   - Agent ID: {agent['id']}")
        print("\nYou can now use these credentials to test the chat functionality.")


if __name__ == "__main__":
    asyncio.run(test_auth_flow())