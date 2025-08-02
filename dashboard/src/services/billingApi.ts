import api from './api';
import { SubscriptionTier } from '../types/billing';

export interface PricingTier {
  id: string;
  name: string;
  price: number;
  features: string[];
  limits: {
    messages: number;
    agents: number;
    api_calls: number;
  };
}

export interface Subscription {
  tier: string;
  status: string;
  current_period_end: string | null;
  usage: {
    messages: number;
    api_calls: number;
    agents: number;
    documents: number;
  };
  limits: {
    messages: number | 'unlimited';
    api_calls: number | 'unlimited';
    agents: number;
  };
}

export interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
}

export const billingApi = {
  // Get pricing tiers
  getPricingTiers: async (): Promise<{ tiers: PricingTier[] }> => {
    const response = await api.get('/billing/pricing');
    return response.data;
  },

  // Get current subscription
  getSubscription: async (): Promise<Subscription> => {
    const response = await api.get('/billing/subscription');
    return response.data;
  },

  // Create or update subscription
  createSubscription: async (tier: SubscriptionTier, paymentMethodId: string) => {
    const response = await api.post('/billing/subscription', {
      tier,
      payment_method_id: paymentMethodId,
    });
    return response.data;
  },

  // Cancel subscription
  cancelSubscription: async () => {
    const response = await api.delete('/billing/subscription');
    return response.data;
  },

  // Get usage statistics
  getUsageStats: async (): Promise<Subscription> => {
    const response = await api.get('/billing/usage');
    return response.data;
  },

  // Get payment methods
  getPaymentMethods: async (): Promise<{ payment_methods: PaymentMethod[] }> => {
    const response = await api.get('/billing/payment-methods');
    return response.data;
  },

  // Add payment method
  addPaymentMethod: async (paymentMethodId: string) => {
    const response = await api.post('/billing/payment-methods', {
      payment_method_id: paymentMethodId,
    });
    return response.data;
  },

  // Create payment intent for Stripe
  createPaymentIntent: async (amount?: number) => {
    const response = await api.post('/billing/payment-intent', {
      amount,
    });
    return response.data;
  },
};