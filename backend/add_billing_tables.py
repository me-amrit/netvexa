"""
Script to add billing tables to the database
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base
from config import settings
from billing_models import Subscription, UsageRecord, Payment, PricingPlan, update_user_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_billing_tables():
    """Add billing tables to the existing database"""
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        # Update User model to include billing relationships
        update_user_model()
        
        # Create billing tables
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from database import User, Agent, ApiKey, Conversation, Message, KnowledgeDocument
            
            # Create only the new billing tables
            await conn.run_sync(Base.metadata.create_all, tables=[
                Subscription.__table__,
                UsageRecord.__table__,
                Payment.__table__,
                PricingPlan.__table__
            ])
        
        logger.info("Billing tables created successfully!")
        
        # Create default pricing plans
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        async_session = sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        
        async with async_session() as session:
            # Check if pricing plans already exist
            from sqlalchemy import select
            existing_plans = await session.execute(select(PricingPlan))
            if not existing_plans.scalars().first():
                # Create default pricing plans
                from billing_models import SubscriptionTier
                from billing_service import PRICING_TIERS
                
                for tier, config in PRICING_TIERS.items():
                    plan = PricingPlan(
                        name=config["name"],
                        tier=tier,
                        monthly_price=config["monthly_price"],
                        message_limit=config["message_limit"],
                        agent_limit=config["agent_limit"],
                        api_calls_limit=config["api_calls_limit"],
                        features=config["features"]
                    )
                    session.add(plan)
                
                await session.commit()
                logger.info("Default pricing plans created!")
        
    except Exception as e:
        logger.error(f"Error creating billing tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_billing_tables())