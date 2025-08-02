# Stripe Setup Guide for NETVEXA

This guide walks through setting up Stripe for the NETVEXA billing system.

## Prerequisites

- Stripe account (create at https://stripe.com)
- Access to Stripe Dashboard

## Setup Steps

### 1. Get API Keys

1. Log in to your Stripe Dashboard
2. Navigate to **Developers** → **API keys**
3. Copy your **Publishable key** (for frontend)
4. Copy your **Secret key** (for backend)

### 2. Create Products and Prices

Create the following products in Stripe Dashboard under **Products**:

#### Pro Plan
- **Name**: NETVEXA Pro
- **Price**: $29/month
- **Billing**: Recurring monthly
- **Features**:
  - 5 AI Agents
  - 50,000 messages/month
  - Advanced analytics
  - Priority support

#### Business Plan
- **Name**: NETVEXA Business
- **Price**: $99/month
- **Billing**: Recurring monthly
- **Features**:
  - 20 AI Agents
  - Unlimited messages
  - Advanced analytics
  - 24/7 priority support

After creating products, copy the **Price IDs** for each plan.

### 3. Configure Webhooks

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Add your endpoint URL: `https://your-domain.com/api/billing/webhook`
4. Select the following events:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Webhook signing secret**

### 4. Update Environment Variables

Add the following to your `.env` file:

```env
# Stripe Configuration
STRIPE_API_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PRO_PRICE_ID=price_your_pro_price_id_here
STRIPE_BUSINESS_PRICE_ID=price_your_business_price_id_here
```

### 5. Frontend Configuration

For the React dashboard, you'll need to:

1. Install Stripe.js: `npm install @stripe/stripe-js`
2. Add your publishable key to the frontend environment
3. Integrate Stripe Elements for payment form

### 6. Test the Integration

#### Test Cards
Use these test card numbers in development:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- Authentication Required: `4000 0025 0000 3155`

#### Test Webhooks Locally
Use Stripe CLI for local webhook testing:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/billing/webhook
```

## Usage Tracking

The billing system tracks:
- **Messages**: Each chat message sent
- **API Calls**: Each API request made
- **Agents**: Number of active agents
- **Documents**: Documents processed

Usage is tracked in real-time and limits are enforced based on subscription tier.

## Subscription Tiers

### Free Tier
- 2 AI Agents
- 5,000 messages/month
- 10,000 API calls/month
- Basic analytics

### Pro Tier ($29/month)
- 5 AI Agents
- 50,000 messages/month
- 100,000 API calls/month
- Advanced analytics
- Priority support

### Business Tier ($99/month)
- 20 AI Agents
- Unlimited messages
- Unlimited API calls
- Advanced analytics
- 24/7 priority support

## Billing Middleware

The billing middleware automatically:
1. Tracks API usage for authenticated users
2. Enforces usage limits based on subscription
3. Returns 429 errors when limits are exceeded
4. Tracks billable events in the database

## Database Schema

The billing system uses these tables:
- `subscriptions`: User subscription details
- `usage_records`: Monthly usage tracking
- `payments`: Payment history
- `pricing_plans`: Available subscription tiers

## Troubleshooting

### Webhook Failures
- Check webhook endpoint is accessible
- Verify webhook secret is correct
- Check server logs for webhook processing errors

### Payment Failures
- Ensure Stripe API key is valid
- Check customer has valid payment method
- Review Stripe Dashboard for detailed error messages

### Usage Tracking Issues
- Verify billing middleware is registered
- Check database connections
- Review usage_records table for tracking data

## Support

For billing-related issues:
- Check Stripe Dashboard for payment details
- Review server logs for API errors
- Contact support with subscription ID and error details