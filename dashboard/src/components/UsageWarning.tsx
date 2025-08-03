import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { billingApi } from '../services/billingApi';

const UsageWarning: React.FC = () => {
  const { data: subscription } = useQuery({
    queryKey: ['subscription'],
    queryFn: billingApi.getSubscription,
    refetchInterval: 60000, // Refetch every minute
  });

  const [dismissed, setDismissed] = React.useState(false);

  if (!subscription || dismissed) {
    return null;
  }

  // Check if any usage is above 80%
  const warnings: string[] = [];

  if (subscription.limits.messages !== 'unlimited') {
    const messageUsage = (subscription.usage.messages / subscription.limits.messages) * 100;
    if (messageUsage >= 80) {
      warnings.push(`Message usage at ${Math.round(messageUsage)}%`);
    }
  }

  if (subscription.limits.api_calls !== 'unlimited') {
    const apiUsage = (subscription.usage.api_calls / subscription.limits.api_calls) * 100;
    if (apiUsage >= 80) {
      warnings.push(`API call usage at ${Math.round(apiUsage)}%`);
    }
  }

  const agentUsage = (subscription.usage.agents / subscription.limits.agents) * 100;
  if (agentUsage >= 80) {
    warnings.push(`Agent limit at ${Math.round(agentUsage)}%`);
  }

  if (warnings.length === 0) {
    return null;
  }

  return (
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" aria-hidden="true" />
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm text-yellow-700">
            <span className="font-medium">Usage Warning:</span> {warnings.join(', ')}
          </p>
          <p className="mt-1 text-sm text-yellow-700">
            <Link to="/billing" className="font-medium underline hover:text-yellow-600">
              Upgrade your plan
            </Link>{' '}
            to increase your limits.
          </p>
        </div>
        <div className="ml-auto pl-3">
          <div className="-mx-1.5 -my-1.5">
            <button
              type="button"
              onClick={() => setDismissed(true)}
              className="inline-flex rounded-md bg-yellow-50 p-1.5 text-yellow-500 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50"
            >
              <span className="sr-only">Dismiss</span>
              <XMarkIcon className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UsageWarning;