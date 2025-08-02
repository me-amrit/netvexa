import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  CreditCardIcon, 
  CheckIcon, 
  XMarkIcon,
  ArrowUpIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { billingApi, PricingTier, Subscription } from '../services/billingApi';
import { SubscriptionTier } from '../types/billing';
import toast from 'react-hot-toast';

const Billing: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedTier, setSelectedTier] = useState<SubscriptionTier | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  // Fetch pricing tiers
  const { data: pricingData } = useQuery('pricing-tiers', billingApi.getPricingTiers);

  // Fetch current subscription
  const { data: subscription, isLoading: subscriptionLoading } = useQuery(
    'subscription',
    billingApi.getSubscription
  );

  // Create/update subscription mutation
  const updateSubscription = useMutation(
    ({ tier, paymentMethodId }: { tier: SubscriptionTier; paymentMethodId: string }) =>
      billingApi.createSubscription(tier, paymentMethodId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('subscription');
        setShowPaymentModal(false);
        toast.success('Subscription updated successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update subscription');
      },
    }
  );

  // Cancel subscription mutation
  const cancelSubscription = useMutation(billingApi.cancelSubscription, {
    onSuccess: () => {
      queryClient.invalidateQueries('subscription');
      toast.success('Subscription will be canceled at the end of the billing period');
    },
    onError: () => {
      toast.error('Failed to cancel subscription');
    },
  });

  const handleUpgrade = (tier: SubscriptionTier) => {
    setSelectedTier(tier);
    setShowPaymentModal(true);
  };

  const getUsagePercentage = (used: number, limit: number | 'unlimited'): number => {
    if (limit === 'unlimited' || limit === -1) return 0;
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage: number): string => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  if (subscriptionLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Current Subscription */}
      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Current Subscription</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-500">Plan</p>
            <p className="text-lg font-semibold capitalize">{subscription?.tier || 'Free'}</p>
            
            <p className="text-sm text-gray-500 mt-4">Status</p>
            <p className="text-lg font-semibold">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                subscription?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {subscription?.status || 'Active'}
              </span>
            </p>
            
            {subscription?.current_period_end && (
              <>
                <p className="text-sm text-gray-500 mt-4">Billing Period Ends</p>
                <p className="text-lg font-semibold">
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
              </>
            )}
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-4">Usage This Month</h3>
            
            {/* Messages Usage */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Messages</span>
                <span>
                  {subscription?.usage.messages || 0} / {
                    subscription?.limits.messages === 'unlimited' 
                      ? '∞' 
                      : subscription?.limits.messages || 0
                  }
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getUsageColor(
                    getUsagePercentage(
                      subscription?.usage.messages || 0,
                      subscription?.limits.messages || 0
                    )
                  )}`}
                  style={{
                    width: `${getUsagePercentage(
                      subscription?.usage.messages || 0,
                      subscription?.limits.messages || 0
                    )}%`,
                  }}
                ></div>
              </div>
            </div>
            
            {/* Agents Usage */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Agents</span>
                <span>
                  {subscription?.usage.agents || 0} / {subscription?.limits.agents || 0}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getUsageColor(
                    getUsagePercentage(
                      subscription?.usage.agents || 0,
                      subscription?.limits.agents || 0
                    )
                  )}`}
                  style={{
                    width: `${getUsagePercentage(
                      subscription?.usage.agents || 0,
                      subscription?.limits.agents || 0
                    )}%`,
                  }}
                ></div>
              </div>
            </div>
            
            {/* API Calls Usage */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>API Calls</span>
                <span>
                  {subscription?.usage.api_calls || 0} / {
                    subscription?.limits.api_calls === 'unlimited'
                      ? '∞'
                      : subscription?.limits.api_calls || 0
                  }
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getUsageColor(
                    getUsagePercentage(
                      subscription?.usage.api_calls || 0,
                      subscription?.limits.api_calls || 0
                    )
                  )}`}
                  style={{
                    width: `${getUsagePercentage(
                      subscription?.usage.api_calls || 0,
                      subscription?.limits.api_calls || 0
                    )}%`,
                  }}
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        {subscription?.tier !== 'free' && (
          <div className="mt-6 pt-6 border-t">
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to cancel your subscription?')) {
                  cancelSubscription.mutate();
                }
              }}
              className="text-red-600 hover:text-red-800 text-sm font-medium"
            >
              Cancel Subscription
            </button>
          </div>
        )}
      </div>

      {/* Pricing Plans */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Pricing Plans</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {pricingData?.tiers.map((tier: PricingTier) => (
            <div
              key={tier.id}
              className={`border rounded-lg p-6 ${
                subscription?.tier === tier.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200'
              }`}
            >
              <h3 className="text-xl font-semibold mb-2">{tier.name}</h3>
              <p className="text-3xl font-bold mb-4">
                ${tier.price}
                <span className="text-base font-normal text-gray-500">/month</span>
              </p>
              
              <ul className="space-y-2 mb-6">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <CheckIcon className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              
              {subscription?.tier === tier.id ? (
                <button
                  disabled
                  className="w-full py-2 px-4 border border-gray-300 rounded-md bg-gray-100 text-gray-500 cursor-not-allowed"
                >
                  Current Plan
                </button>
              ) : tier.price === 0 ? (
                <button
                  onClick={() => handleUpgrade(tier.id as SubscriptionTier)}
                  className="w-full py-2 px-4 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Downgrade
                </button>
              ) : (
                <button
                  onClick={() => handleUpgrade(tier.id as SubscriptionTier)}
                  className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                >
                  Upgrade
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Payment Modal (placeholder - would integrate with Stripe Elements) */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Update Subscription</h3>
            <p className="text-gray-600 mb-4">
              Payment integration with Stripe would go here.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowPaymentModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // In production, this would handle Stripe payment
                  toast.info('Stripe payment integration needed');
                  setShowPaymentModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Billing;