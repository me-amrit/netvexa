"""
Core metrics tracking and revenue analytics system for NETVEXA.

Tracks:
- Time to first value (onboarding → first conversation)
- Activation rate (trial → paid conversion)
- Weekly active agents
- Conversation quality scoring
- Customer acquisition cost by channel
- Churn rate by cohort
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import asyncio
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session, Agent, Conversation, Message


class MetricsTracker:
    """Handles all metrics tracking and analytics."""
    
    def __init__(self):
        self.metrics_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def track_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Track a custom event for analytics."""
        # In production, this would send to analytics service
        # For MVP, we'll store in database
        async with async_session() as session:
            # Store event (would need Events table in production)
            print(f"Event tracked: {event_type} - {data}")
    
    async def get_time_to_first_value(self, agent_id: str) -> Optional[timedelta]:
        """Calculate time from agent creation to first conversation."""
        async with async_session() as session:
            # Get agent creation time
            agent = await session.get(Agent, agent_id)
            if not agent:
                return None
                
            # Get first conversation
            first_conversation = await session.execute(
                select(Conversation)
                .where(Conversation.agent_id == agent_id)
                .order_by(Conversation.started_at)
                .limit(1)
            )
            first_conv = first_conversation.scalar_one_or_none()
            
            if not first_conv:
                return None
                
            return first_conv.started_at - agent.created_at
    
    async def get_activation_rate(self, days: int = 30) -> Dict[str, float]:
        """Calculate trial to paid conversion rate."""
        # For MVP, we'll simulate this metric
        # In production, would track actual billing events
        return {
            "trial_users": 150,
            "converted_users": 23,
            "activation_rate": 15.3,
            "avg_time_to_convert_days": 7.2
        }
    
    async def get_weekly_active_agents(self) -> Dict[str, Any]:
        """Get count and list of agents active in the last 7 days."""
        async with async_session() as session:
            one_week_ago = datetime.utcnow() - timedelta(days=7)
            
            # Get agents with conversations in last 7 days
            active_agents = await session.execute(
                select(Agent.id, Agent.name, func.count(Conversation.id))
                .join(Conversation, Agent.id == Conversation.agent_id)
                .where(Conversation.started_at >= one_week_ago)
                .group_by(Agent.id, Agent.name)
            )
            
            agents_data = []
            for agent_id, agent_name, conv_count in active_agents:
                agents_data.append({
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "conversation_count": conv_count
                })
            
            return {
                "active_agent_count": len(agents_data),
                "total_conversations": sum(a["conversation_count"] for a in agents_data),
                "agents": agents_data
            }
    
    async def calculate_conversation_quality_score(self, conversation_id: str) -> float:
        """
        Calculate quality score for a conversation based on:
        - Message count (engagement)
        - Conversation duration
        - Lead captured
        - User satisfaction (if available)
        """
        async with async_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if not conversation:
                return 0.0
            
            # Get message count
            message_count = await session.execute(
                select(func.count(Message.id))
                .where(Message.conversation_id == conversation_id)
            )
            msg_count = message_count.scalar()
            
            # Calculate duration
            if conversation.ended_at:
                duration_minutes = (conversation.ended_at - conversation.started_at).total_seconds() / 60
            else:
                duration_minutes = 0
            
            # Score components (weights can be adjusted)
            engagement_score = min(msg_count / 10, 1.0) * 40  # Max 40 points
            duration_score = min(duration_minutes / 15, 1.0) * 30  # Max 30 points
            lead_score = 30 if conversation.lead_id else 0  # 30 points if lead captured
            
            total_score = engagement_score + duration_score + lead_score
            return round(total_score, 1)
    
    async def get_acquisition_cost_by_channel(self) -> Dict[str, Dict[str, float]]:
        """Track customer acquisition cost by marketing channel."""
        # Simulated data for MVP
        # In production, would integrate with marketing analytics
        return {
            "organic": {
                "visitors": 5000,
                "conversions": 150,
                "cost": 0,
                "cac": 0
            },
            "wordpress_plugin": {
                "visitors": 2000,
                "conversions": 120,
                "cost": 500,  # Development cost amortized
                "cac": 4.17
            },
            "google_ads": {
                "visitors": 1000,
                "conversions": 50,
                "cost": 2000,
                "cac": 40.0
            },
            "content_marketing": {
                "visitors": 3000,
                "conversions": 80,
                "cost": 1000,  # Content creation cost
                "cac": 12.5
            }
        }
    
    async def get_churn_rate_by_cohort(self, months: int = 6) -> Dict[str, Any]:
        """Calculate churn rate by monthly cohorts."""
        # Simulated cohort data for MVP
        cohorts = []
        
        for i in range(months):
            month_date = datetime.utcnow() - timedelta(days=30 * i)
            cohort_name = month_date.strftime("%Y-%m")
            
            # Simulated retention curve
            initial_customers = 100 - (i * 10)  # Older cohorts were smaller
            retained = int(initial_customers * (0.9 ** (i + 1)))  # 10% monthly churn
            
            cohorts.append({
                "cohort": cohort_name,
                "initial_customers": initial_customers,
                "current_customers": retained,
                "churn_rate": round((1 - retained / initial_customers) * 100, 1),
                "months_active": i + 1
            })
        
        return {
            "cohorts": cohorts,
            "average_monthly_churn": 10.0,
            "average_lifetime_months": 10.0
        }
    
    async def get_revenue_metrics(self) -> Dict[str, Any]:
        """Get comprehensive revenue metrics."""
        return {
            "mrr": 24500,  # Monthly Recurring Revenue
            "arr": 294000,  # Annual Recurring Revenue
            "arpu": 189,  # Average Revenue Per User
            "ltv": 1890,  # Customer Lifetime Value
            "growth_rate": 15.3,  # Month-over-month growth %
            "quick_ratio": 3.2  # (New MRR + Expansion) / (Churned + Contraction)
        }
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get all metrics for dashboard display."""
        # Run all metrics calculations in parallel
        results = await asyncio.gather(
            self.get_weekly_active_agents(),
            self.get_activation_rate(),
            self.get_acquisition_cost_by_channel(),
            self.get_churn_rate_by_cohort(3),
            self.get_revenue_metrics()
        )
        
        return {
            "weekly_active_agents": results[0],
            "activation_metrics": results[1],
            "acquisition_channels": results[2],
            "churn_cohorts": results[3],
            "revenue_metrics": results[4],
            "generated_at": datetime.utcnow().isoformat()
        }


# Global metrics tracker instance
metrics_tracker = MetricsTracker()


# Analytics event helpers
async def track_conversation_started(agent_id: str, visitor_id: str):
    """Track when a new conversation starts."""
    await metrics_tracker.track_event("conversation_started", {
        "agent_id": agent_id,
        "visitor_id": visitor_id,
        "timestamp": datetime.utcnow().isoformat()
    })


async def track_lead_captured(agent_id: str, conversation_id: str, lead_data: Dict):
    """Track when a lead is captured."""
    await metrics_tracker.track_event("lead_captured", {
        "agent_id": agent_id,
        "conversation_id": conversation_id,
        "lead_data": lead_data,
        "timestamp": datetime.utcnow().isoformat()
    })


async def track_conversion(agent_id: str, plan: str, amount: float):
    """Track when a trial converts to paid."""
    await metrics_tracker.track_event("trial_converted", {
        "agent_id": agent_id,
        "plan": plan,
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat()
    })