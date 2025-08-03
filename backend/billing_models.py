"""
Billing and subscription models for NETVEXA
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from database import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    PRO = "pro"
    BUSINESS = "business"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    
    # Subscription details
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(String, default="active")  # active, canceled, past_due, etc.
    
    # Billing cycle
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Usage limits based on tier
    message_limit = Column(Integer, default=5000)  # Monthly message limit
    agent_limit = Column(Integer, default=5)       # Number of agents allowed
    api_calls_limit = Column(Integer, default=10000)  # API calls per month
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")


class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Usage tracking
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metrics
    messages_sent = Column(Integer, default=0)
    api_calls_made = Column(Integer, default=0)
    agents_created = Column(Integer, default=0)
    documents_processed = Column(Integer, default=0)
    
    # Additional metrics as JSON
    additional_metrics = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")
    user = relationship("User", back_populates="usage_records")


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Stripe payment details
    stripe_payment_intent_id = Column(String, unique=True, index=True)
    stripe_invoice_id = Column(String, index=True)
    
    # Payment details
    amount = Column(Float, nullable=False)  # Amount in dollars
    currency = Column(String, default="usd")
    status = Column(Enum(PaymentStatus), nullable=False)
    description = Column(String)
    
    # Billing details
    billing_period_start = Column(DateTime(timezone=True))
    billing_period_end = Column(DateTime(timezone=True))
    
    # Metadata
    meta_data = Column(JSON, default={})  # Renamed to avoid SQLAlchemy conflict
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True))
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User", back_populates="payments")


class PricingPlan(Base):
    """Defines available pricing plans"""
    __tablename__ = "pricing_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    tier = Column(Enum(SubscriptionTier), unique=True, nullable=False)
    
    # Pricing
    monthly_price = Column(Float, nullable=False)
    annual_price = Column(Float)  # Optional annual discount
    
    # Limits
    message_limit = Column(Integer, nullable=False)
    agent_limit = Column(Integer, nullable=False)
    api_calls_limit = Column(Integer, nullable=False)
    document_limit = Column(Integer)  # Documents per agent
    
    # Features as JSON
    features = Column(JSON, default=[])
    
    # Stripe product/price IDs
    stripe_product_id = Column(String)
    stripe_monthly_price_id = Column(String)
    stripe_annual_price_id = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Update User model to include subscription relationship
def update_user_model():
    """This function should be called to add subscription relationship to User model"""
    from database import User
    if not hasattr(User, 'subscription'):
        User.subscription = relationship("Subscription", back_populates="user", uselist=False)
    if not hasattr(User, 'usage_records'):
        User.usage_records = relationship("UsageRecord", back_populates="user")
    if not hasattr(User, 'payments'):
        User.payments = relationship("Payment", back_populates="user")