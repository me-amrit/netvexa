# NETVEXA Pricing Synchronization Guide

This document tracks all files that contain pricing information to ensure consistency across the platform.

## Current Pricing Tiers

| Tier | Price | Agents | Messages | Key Features |
|------|-------|---------|----------|--------------|
| **Starter** | €79/mo | 1 | 2,000 | Basic analytics, Email support, WordPress plugin |
| **Growth** | €199/mo | 2 | 8,000 | Advanced analytics, Priority support, Custom branding, API access |
| **Professional** | €499/mo | 5 | 25,000 | A/B testing, Team collaboration (3 seats) |
| **Business** | €999/mo | 15 | 60,000 | 24/7 support, Custom integrations, Team (10 seats), SLA |

## Files to Keep in Sync

### 1. Backend Implementation
- **`/backend/billing_service.py`** (lines 40-104)
  - Source of truth for pricing
  - Contains tier definitions, limits, and features
  - Used by billing system

### 2. Frontend Display
- **`/homepage/components/Pricing.tsx`** (lines 2-67)
  - Public website pricing display
  - Must match backend exactly
  - ✅ Updated: August 3, 2025

### 3. Documentation
- **`/docs/revised-pricing-strategy.md`**
  - Has different pricing (needs update)
  - Shows $0, $149, $499, Custom tiers

### 4. Database Schema
- **`/backend/database.py`**
  - SubscriptionTier enum definition
  - Must include: STARTER, GROWTH, PRO, BUSINESS

## Checklist for Pricing Changes

When updating pricing, update ALL of these files:

- [ ] `/backend/billing_service.py` - Update TIER_DETAILS
- [ ] `/homepage/components/Pricing.tsx` - Update plans array
- [ ] `/docs/revised-pricing-strategy.md` - Update documentation
- [ ] `/backend/database.py` - Update enum if adding/removing tiers
- [ ] Run tests to ensure billing calculations work
- [ ] Update Stripe price IDs in environment variables

## Environment Variables

These need to be set for production:
```
STRIPE_STARTER_PRICE_ID=price_xxxxx
STRIPE_GROWTH_PRICE_ID=price_xxxxx
STRIPE_PRO_PRICE_ID=price_xxxxx
STRIPE_BUSINESS_PRICE_ID=price_xxxxx
```

## Notes

1. The "Professional" tier in billing_service.py is referenced as "PRO" in the enum
2. Prices are in EUR (€) not USD ($)
3. Message limits are enforced by the billing middleware
4. Agent limits are checked when creating new agents