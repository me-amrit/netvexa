"""
Billing API routes for subscription and payment management
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import os

from database import get_db
from auth import get_current_user
from billing_service import BillingService, PRICING_TIERS
from billing_models import SubscriptionTier

router = APIRouter(prefix="/api/billing", tags=["billing"])
logger = logging.getLogger(__name__)


class CreateSubscriptionRequest(BaseModel):
    tier: SubscriptionTier
    payment_method_id: str


class UpdatePaymentMethodRequest(BaseModel):
    payment_method_id: str


class CreatePaymentIntentRequest(BaseModel):
    amount: Optional[float] = None  # For one-time payments


@router.get("/pricing")
async def get_pricing_tiers():
    """Get all available pricing tiers"""
    return {
        "tiers": [
            {
                "id": tier.value,
                "name": config["name"],
                "price": config["monthly_price"],
                "features": config["features"],
                "limits": {
                    "messages": config["message_limit"],
                    "agents": config["agent_limit"],
                    "api_calls": config["api_calls_limit"]
                }
            }
            for tier, config in PRICING_TIERS.items()
        ]
    }


@router.get("/subscription")
async def get_subscription(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription details"""
    try:
        stats = await BillingService.get_usage_stats(current_user["id"], db)
        return stats
    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription")


@router.post("/subscription")
async def create_or_update_subscription(
    request: CreateSubscriptionRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update a subscription"""
    try:
        result = await BillingService.create_subscription(
            user_id=current_user["id"],
            tier=request.tier,
            payment_method_id=request.payment_method_id,
            db=db
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")


@router.delete("/subscription")
async def cancel_subscription(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel the current subscription"""
    try:
        success = await BillingService.cancel_subscription(current_user["id"], db)
        if success:
            return {"message": "Subscription will be canceled at the end of the billing period"}
        else:
            raise HTTPException(status_code=404, detail="No active subscription found")
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.get("/usage")
async def get_usage_stats(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed usage statistics for the current billing period"""
    try:
        stats = await BillingService.get_usage_stats(current_user["id"], db)
        return stats
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch usage statistics")


@router.get("/payment-methods")
async def get_payment_methods(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's saved payment methods from Stripe"""
    try:
        # Get user's Stripe customer ID from subscription
        from sqlalchemy import select
        from billing_models import Subscription
        
        subscription = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user["id"])
        )
        subscription = subscription.scalar_one_or_none()
        
        if not subscription or not subscription.stripe_customer_id:
            return {"payment_methods": []}
        
        # Get payment methods from Stripe
        import stripe
        payment_methods = stripe.PaymentMethod.list(
            customer=subscription.stripe_customer_id,
            type="card"
        )
        
        return {
            "payment_methods": [
                {
                    "id": pm.id,
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year
                }
                for pm in payment_methods.data
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching payment methods: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment methods")


@router.post("/payment-methods")
async def add_payment_method(
    request: UpdatePaymentMethodRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new payment method"""
    try:
        # Get or create Stripe customer
        from sqlalchemy import select
        from billing_models import Subscription
        from database import User
        
        subscription = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user["id"])
        )
        subscription = subscription.scalar_one_or_none()
        
        if not subscription:
            user = await db.get(User, current_user["id"])
            customer_id = await BillingService.create_stripe_customer(user, db)
        else:
            customer_id = subscription.stripe_customer_id
        
        # Attach payment method
        import stripe
        stripe.PaymentMethod.attach(
            request.payment_method_id,
            customer=customer_id
        )
        
        return {"message": "Payment method added successfully"}
    except Exception as e:
        logger.error(f"Error adding payment method: {e}")
        raise HTTPException(status_code=500, detail="Failed to add payment method")


@router.post("/payment-intent")
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a payment intent for one-time payments or setup"""
    try:
        import stripe
        from sqlalchemy import select
        from billing_models import Subscription
        
        # Get customer ID
        subscription = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user["id"])
        )
        subscription = subscription.scalar_one_or_none()
        
        if not subscription:
            from database import User
            user = await db.get(User, current_user["id"])
            customer_id = await BillingService.create_stripe_customer(user, db)
        else:
            customer_id = subscription.stripe_customer_id
        
        # Create payment intent
        if request.amount:
            # One-time payment
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency="usd",
                customer=customer_id,
                metadata={"user_id": current_user["id"]}
            )
        else:
            # Setup intent for saving payment method
            intent = stripe.SetupIntent.create(
                customer=customer_id,
                metadata={"user_id": current_user["id"]}
            )
        
        return {"client_secret": intent.client_secret}
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment intent")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        import stripe
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle different event types
        if event["type"] == "invoice.payment_succeeded":
            # Payment successful - update subscription status
            invoice = event["data"]["object"]
            await handle_successful_payment(invoice, db)
        
        elif event["type"] == "invoice.payment_failed":
            # Payment failed - update subscription status
            invoice = event["data"]["object"]
            await handle_failed_payment(invoice, db)
        
        elif event["type"] == "customer.subscription.updated":
            # Subscription updated - sync with database
            subscription = event["data"]["object"]
            await sync_subscription_status(subscription, db)
        
        elif event["type"] == "customer.subscription.deleted":
            # Subscription canceled - update database
            subscription = event["data"]["object"]
            await handle_subscription_cancellation(subscription, db)
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


# Helper functions for webhook handling
async def handle_successful_payment(invoice: Dict, db: AsyncSession):
    """Handle successful payment from Stripe"""
    from sqlalchemy import select
    from billing_models import Subscription, Payment, PaymentStatus
    from datetime import datetime
    
    # Find subscription by Stripe customer ID
    subscription = await db.execute(
        select(Subscription).where(
            Subscription.stripe_customer_id == invoice["customer"]
        )
    )
    subscription = subscription.scalar_one_or_none()
    
    if subscription:
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            stripe_invoice_id=invoice["id"],
            stripe_payment_intent_id=invoice["payment_intent"],
            amount=invoice["amount_paid"] / 100,  # Convert from cents
            currency=invoice["currency"],
            status=PaymentStatus.SUCCEEDED,
            description=f"Subscription payment for {subscription.tier.value}",
            billing_period_start=datetime.fromtimestamp(invoice["period_start"]),
            billing_period_end=datetime.fromtimestamp(invoice["period_end"]),
            paid_at=datetime.fromtimestamp(invoice["status_transitions"]["paid_at"])
        )
        db.add(payment)
        
        # Update subscription status
        subscription.status = "active"
        await db.commit()


async def handle_failed_payment(invoice: Dict, db: AsyncSession):
    """Handle failed payment from Stripe"""
    from sqlalchemy import select
    from billing_models import Subscription, Payment, PaymentStatus
    from datetime import datetime
    
    subscription = await db.execute(
        select(Subscription).where(
            Subscription.stripe_customer_id == invoice["customer"]
        )
    )
    subscription = subscription.scalar_one_or_none()
    
    if subscription:
        # Create failed payment record
        payment = Payment(
            subscription_id=subscription.id,
            user_id=subscription.user_id,
            stripe_invoice_id=invoice["id"],
            amount=invoice["amount_due"] / 100,
            currency=invoice["currency"],
            status=PaymentStatus.FAILED,
            description=f"Failed payment for {subscription.tier.value}",
            billing_period_start=datetime.fromtimestamp(invoice["period_start"]),
            billing_period_end=datetime.fromtimestamp(invoice["period_end"])
        )
        db.add(payment)
        
        # Update subscription status
        subscription.status = "past_due"
        await db.commit()


async def sync_subscription_status(stripe_subscription: Dict, db: AsyncSession):
    """Sync subscription status from Stripe"""
    from sqlalchemy import select
    from billing_models import Subscription
    from datetime import datetime
    
    subscription = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = subscription.scalar_one_or_none()
    
    if subscription:
        subscription.status = stripe_subscription["status"]
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription["current_period_start"]
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription["current_period_end"]
        )
        subscription.cancel_at_period_end = stripe_subscription["cancel_at_period_end"]
        await db.commit()


async def handle_subscription_cancellation(stripe_subscription: Dict, db: AsyncSession):
    """Handle subscription cancellation from Stripe"""
    from sqlalchemy import select
    from billing_models import Subscription, SubscriptionTier
    
    subscription = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_subscription["id"]
        )
    )
    subscription = subscription.scalar_one_or_none()
    
    if subscription:
        # Downgrade to free tier
        subscription.tier = SubscriptionTier.FREE
        subscription.status = "active"
        subscription.stripe_subscription_id = None
        subscription.message_limit = PRICING_TIERS[SubscriptionTier.FREE]["message_limit"]
        subscription.agent_limit = PRICING_TIERS[SubscriptionTier.FREE]["agent_limit"]
        subscription.api_calls_limit = PRICING_TIERS[SubscriptionTier.FREE]["api_calls_limit"]
        await db.commit()