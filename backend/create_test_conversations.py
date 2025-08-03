#!/usr/bin/env python3
"""
Script to create test conversations for development/testing
"""

import asyncio
import sys
from datetime import datetime, timedelta
from database import init_db, async_session, Agent, Conversation, Message, User
from sqlalchemy import select

async def create_test_conversations():
    """Create test conversations for the first agent found"""
    await init_db()
    
    async with async_session() as session:
        # Get the first user and agent
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("No users found. Please create a user first.")
            return
        
        agent_result = await session.execute(
            select(Agent).where(Agent.user_id == user.id).limit(1)
        )
        agent = agent_result.scalar_one_or_none()
        
        if not agent:
            print(f"No agents found for user {user.email}")
            return
        
        print(f"Creating test conversations for agent '{agent.name}' (ID: {agent.id})")
        
        # Create 5 test conversations
        conversations_data = [
            {
                "visitor_id": "visitor_1",
                "messages": [
                    ("user", "Hello! Can you help me with your pricing?"),
                    ("agent", "Of course! I'd be happy to help you understand our pricing tiers. We offer four plans: Starter (€79/mo), Growth (€199/mo), Professional (€499/mo), and Business (€999/mo). Which one interests you most?"),
                    ("user", "What's included in the Starter plan?"),
                    ("agent", "The Starter plan includes 1 AI Agent, 2,000 messages per month, basic analytics, email support, and our WordPress plugin. It's perfect for small businesses getting started!"),
                ]
            },
            {
                "visitor_id": "visitor_2", 
                "messages": [
                    ("user", "Hi, I'm interested in the WordPress integration"),
                    ("agent", "Great! Our WordPress plugin makes it super easy to add AI-powered chat to your website. You can install it directly from the WordPress plugin directory. Would you like me to walk you through the setup?"),
                    ("user", "Yes please!"),
                    ("agent", "Perfect! Here are the steps: 1) Install the NETVEXA plugin from WordPress admin, 2) Get your agent embed code from our dashboard, 3) Configure the plugin with your agent ID. The whole process takes less than 5 minutes!"),
                ]
            },
            {
                "visitor_id": "visitor_3",
                "messages": [
                    ("user", "What kind of analytics do you provide?"),
                    ("agent", "We provide comprehensive analytics including conversation volume, response times, customer satisfaction scores, lead capture rates, and peak usage hours. Professional and Business plans also include A/B testing capabilities and custom reporting."),
                ]
            },
            {
                "visitor_id": "visitor_4",
                "messages": [
                    ("user", "Do you support multiple languages?"),
                    ("agent", "Yes! Our AI agents can communicate in multiple languages including English, Spanish, French, German, Italian, and many more. You can configure the primary language for your agent in the dashboard settings."),
                    ("user", "That's perfect for our international customers"),
                    ("agent", "Exactly! Many of our customers use multi-language support to serve global audiences. The AI automatically detects the customer's language and responds appropriately."),
                ]
            },
            {
                "visitor_id": "visitor_5",
                "messages": [
                    ("user", "How quickly can I get started?"),
                    ("agent", "You can get started in just a few minutes! Simply sign up, create your first agent, upload some knowledge documents, and deploy. Most customers are up and running within 15 minutes."),
                ]
            }
        ]
        
        for i, conv_data in enumerate(conversations_data):
            # Create conversation with staggered timestamps
            start_time = datetime.utcnow() - timedelta(days=i+1, hours=i*2)
            
            conversation = Conversation(
                agent_id=agent.id,
                visitor_id=conv_data["visitor_id"],
                started_at=start_time,
                ended_at=start_time + timedelta(minutes=len(conv_data["messages"]) * 2),
                meta_data={"source": "test_data", "test_user": True}
            )
            session.add(conversation)
            await session.flush()  # Get the conversation ID
            
            # Add messages
            for j, (sender, content) in enumerate(conv_data["messages"]):
                message_time = start_time + timedelta(minutes=j*2)
                message = Message(
                    conversation_id=conversation.id,
                    sender=sender,
                    content=content,
                    timestamp=message_time
                )
                session.add(message)
            
            print(f"Created conversation {i+1} with {len(conv_data['messages'])} messages")
        
        await session.commit()
        print(f"\n✅ Successfully created {len(conversations_data)} test conversations!")
        print(f"Agent: {agent.name} (ID: {agent.id})")
        print("You can now see these conversations in the dashboard.")

if __name__ == "__main__":
    try:
        asyncio.run(create_test_conversations())
    except KeyboardInterrupt:
        print("\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)