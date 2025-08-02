"""
Billing service for handling Stripe integration and usage tracking
"""
import os
import stripe
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from billing_models import (
    Subscription, SubscriptionTier, UsageRecord, Payment, 
    PaymentStatus, PricingPlan, update_user_model
)
from database import User, get_db
from config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY

logger = logging.getLogger(__name__)

# Pricing configuration
PRICING_TIERS = {
    SubscriptionTier.FREE: {
        "name": "Free Trial",
        "monthly_price": 0,
        "message_limit": 500,
        "agent_limit": 1,
        "api_calls_limit": 1000,
        "features": [
            "1 AI Agent",
            "500 messages/month",
            "Basic analytics",
            "Community support",
            "14-day trial only"
        ]
    },
    SubscriptionTier.STARTER: {
        "name": "Starter",
        "monthly_price": 79,
        "message_limit": 2000,
        "agent_limit": 1,
        "api_calls_limit": 5000,
        "stripe_price_id": os.getenv("STRIPE_STARTER_PRICE_ID"),
        "features": [
            "1 AI Agent",
            "2,000 messages/month",
            "Basic analytics",
            "Email support",
            "WordPress plugin"
        ]
    },
    SubscriptionTier.GROWTH: {
        "name": "Growth",
        "monthly_price": 199,
        "message_limit": 8000,
        "agent_limit": 2,
        "api_calls_limit": 20000,
        "stripe_price_id": os.getenv("STRIPE_GROWTH_PRICE_ID"),
        "features": [
            "2 AI Agents",
            "8,000 messages/month",
            "Advanced analytics",
            "Priority email support",
            "Custom branding",
            "API access"
        ]
    },
    SubscriptionTier.PRO: {
        "name": "Professional",
        "monthly_price": 499,
        "message_limit": 25000,
        "agent_limit": 5,
        "api_calls_limit": 50000,
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
        "features": [
            "5 AI Agents",
            "25,000 messages/month",
            "Advanced analytics",
            "Priority support",
            "A/B testing",
            "Team collaboration (3 seats)"
        ]
    },
    SubscriptionTier.BUSINESS: {
        "name": "Business",
        "monthly_price": 999,
        "message_limit": 60000,
        "agent_limit": 15,
        "api_calls_limit": 150000,
        "stripe_price_id": os.getenv("STRIPE_BUSINESS_PRICE_ID"),
        "features": [
            "15 AI Agents",
            "60,000 messages/month",
            "Advanced analytics & reporting",
            "24/7 priority support",
            "Custom integrations",
            "Team collaboration (10 seats)",
            "SLA guarantee"
        ]
    }
}


class BillingService:
    """Service for handling billing operations"""
    
    @staticmethod
    async def create_stripe_customer(user: User, db: AsyncSession) -> str:
        """Create a Stripe customer for a user"""
        try:
            # Create Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                metadata={
                    "user_id": user.id,
                    "company_name": user.company_name
                }
            )
            
            # Create subscription record with free tier
            subscription = Subscription(
                user_id=user.id,
                stripe_customer_id=customer.id,
                tier=SubscriptionTier.FREE,
                status="active",
                message_limit=PRICING_TIERS[SubscriptionTier.FREE]["message_limit"],
                agent_limit=PRICING_TIERS[SubscriptionTier.FREE]["agent_limit"],
                api_calls_limit=PRICING_TIERS[SubscriptionTier.FREE]["api_calls_limit"],
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            
            db.add(subscription)
            await db.commit()
            
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return customer.id
            
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise
    
    @staticmethod
    async def create_subscription(
        user_id: str,
        tier: SubscriptionTier,
        payment_method_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Create or update a subscription"""
        try:
            # Get user and existing subscription
            user = await db.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            
            subscription = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = subscription.scalar_one_or_none()
            
            if not subscription:
                # Create new subscription
                customer_id = await BillingService.create_stripe_customer(user, db)
            else:
                customer_id = subscription.stripe_customer_id
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )
            
            # Create or update Stripe subscription
            tier_config = PRICING_TIERS[tier]
            if tier == SubscriptionTier.FREE:
                # Free tier - no Stripe subscription needed
                if subscription:
                    subscription.tier = tier
                    subscription.status = "active"
                    subscription.message_limit = tier_config["message_limit"]
                    subscription.agent_limit = tier_config["agent_limit"]
                    subscription.api_calls_limit = tier_config["api_calls_limit"]
                    await db.commit()
                
                return {"status": "success", "subscription_id": subscription.id}
            
            # Create Stripe subscription for paid tiers
            stripe_sub = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": tier_config["stripe_price_id"]}],
                expand=["latest_invoice.payment_intent"]
            )
            
            # Update database subscription
            if subscription:
                subscription.stripe_subscription_id = stripe_sub.id
                subscription.tier = tier
                subscription.status = stripe_sub.status
                subscription.message_limit = tier_config["message_limit"]
                subscription.agent_limit = tier_config["agent_limit"]
                subscription.api_calls_limit = tier_config["api_calls_limit"]
                subscription.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
            else:
                subscription = Subscription(
                    user_id=user_id,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=stripe_sub.id,
                    tier=tier,
                    status=stripe_sub.status,
                    message_limit=tier_config["message_limit"],
                    agent_limit=tier_config["agent_limit"],
                    api_calls_limit=tier_config["api_calls_limit"],
                    current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
                    current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end)
                )
                db.add(subscription)
            
            await db.commit()
            
            return {
                "status": "success",
                "subscription_id": subscription.id,
                "stripe_subscription_id": stripe_sub.id,
                "client_secret": stripe_sub.latest_invoice.payment_intent.client_secret
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
    
    @staticmethod
    async def cancel_subscription(user_id: str, db: AsyncSession) -> bool:
        """Cancel a subscription"""
        try:
            subscription = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = subscription.scalar_one_or_none()
            
            if not subscription:
                return False
            
            if subscription.stripe_subscription_id:
                # Cancel Stripe subscription at period end
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            
            subscription.cancel_at_period_end = True
            await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            raise
    
    @staticmethod
    async def track_usage(
        user_id: str,
        usage_type: str,
        amount: int = 1,
        db: AsyncSession
    ) -> None:
        """Track usage for a user"""
        try:
            # Get current usage record
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            usage_record = await db.execute(
                select(UsageRecord).where(
                    and_(
                        UsageRecord.user_id == user_id,
                        UsageRecord.period_start == period_start
                    )
                )
            )
            usage_record = usage_record.scalar_one_or_none()
            
            if not usage_record:
                # Get subscription
                subscription = await db.execute(
                    select(Subscription).where(Subscription.user_id == user_id)
                )
                subscription = subscription.scalar_one()
                
                usage_record = UsageRecord(
                    subscription_id=subscription.id,
                    user_id=user_id,
                    period_start=period_start,
                    period_end=period_end
                )
                db.add(usage_record)
            
            # Update usage based on type
            if usage_type == "message":
                usage_record.messages_sent += amount
            elif usage_type == "api_call":
                usage_record.api_calls_made += amount
            elif usage_type == "agent_created":
                usage_record.agents_created += amount
            elif usage_type == "document_processed":
                usage_record.documents_processed += amount
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            # Don't raise - we don't want usage tracking failures to break the app
    
    @staticmethod
    async def check_usage_limits(user_id: str, usage_type: str, db: AsyncSession) -> bool:
        """Check if user has exceeded usage limits"""
        try:
            # Get subscription
            subscription = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = subscription.scalar_one_or_none()
            
            if not subscription:
                return False  # No subscription, deny access
            
            # Free tier always has limits
            if subscription.tier == SubscriptionTier.FREE:
                # Get current usage
                now = datetime.utcnow()
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                usage_record = await db.execute(
                    select(UsageRecord).where(
                        and_(
                            UsageRecord.user_id == user_id,
                            UsageRecord.period_start == period_start
                        )
                    )
                )
                usage_record = usage_record.scalar_one_or_none()
                
                if not usage_record:
                    return True  # No usage yet
                
                # Check limits based on type
                if usage_type == "message":
                    return usage_record.messages_sent < subscription.message_limit
                elif usage_type == "api_call":
                    return usage_record.api_calls_made < subscription.api_calls_limit
                elif usage_type == "agent":
                    # Count active agents
                    from database import Agent
                    agent_count = await db.execute(
                        select(Agent).where(
                            and_(
                                Agent.user_id == user_id,
                                Agent.is_active == True
                            )
                        )
                    )
                    agent_count = len(agent_count.scalars().all())
                    return agent_count < subscription.agent_limit
            
            # Business tier has unlimited messages/API calls
            elif subscription.tier == SubscriptionTier.BUSINESS:
                if usage_type in ["message", "api_call"]:
                    return True
                elif usage_type == "agent":
                    # Still has agent limit
                    from database import Agent
                    agent_count = await db.execute(
                        select(Agent).where(
                            and_(
                                Agent.user_id == user_id,
                                Agent.is_active == True
                            )
                        )
                    )
                    agent_count = len(agent_count.scalars().all())
                    return agent_count < subscription.agent_limit
            
            # Pro tier has all limits
            else:
                # Similar to free tier logic
                now = datetime.utcnow()
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                usage_record = await db.execute(
                    select(UsageRecord).where(
                        and_(
                            UsageRecord.user_id == user_id,
                            UsageRecord.period_start == period_start
                        )
                    )
                )
                usage_record = usage_record.scalar_one_or_none()
                
                if not usage_record:
                    return True
                
                if usage_type == "message":
                    return usage_record.messages_sent < subscription.message_limit
                elif usage_type == "api_call":
                    return usage_record.api_calls_made < subscription.api_calls_limit
                elif usage_type == "agent":
                    from database import Agent
                    agent_count = await db.execute(
                        select(Agent).where(
                            and_(
                                Agent.user_id == user_id,
                                Agent.is_active == True
                            )
                        )
                    )
                    agent_count = len(agent_count.scalars().all())
                    return agent_count < subscription.agent_limit
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return False  # Deny on error
    
    @staticmethod
    async def get_usage_stats(user_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        try:
            # Get subscription
            subscription = await db.execute(
                select(Subscription).where(Subscription.user_id == user_id)
            )
            subscription = subscription.scalar_one_or_none()
            
            if not subscription:
                return {
                    "tier": "none",
                    "usage": {},
                    "limits": {}
                }
            
            # Get current usage
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_record = await db.execute(
                select(UsageRecord).where(
                    and_(
                        UsageRecord.user_id == user_id,
                        UsageRecord.period_start == period_start
                    )
                )
            )
            usage_record = usage_record.scalar_one_or_none()
            
            # Count active agents
            from database import Agent
            agent_count = await db.execute(
                select(Agent).where(
                    and_(
                        Agent.user_id == user_id,
                        Agent.is_active == True
                    )
                )
            )
            agent_count = len(agent_count.scalars().all())
            
            return {
                "tier": subscription.tier.value,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                "usage": {
                    "messages": usage_record.messages_sent if usage_record else 0,
                    "api_calls": usage_record.api_calls_made if usage_record else 0,
                    "agents": agent_count,
                    "documents": usage_record.documents_processed if usage_record else 0
                },
                "limits": {
                    "messages": subscription.message_limit if subscription.message_limit != -1 else "unlimited",
                    "api_calls": subscription.api_calls_limit if subscription.api_calls_limit != -1 else "unlimited",
                    "agents": subscription.agent_limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            raise