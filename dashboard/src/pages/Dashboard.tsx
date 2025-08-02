import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  ChartBarIcon, 
  ChatBubbleBottomCenterTextIcon,
  UserGroupIcon,
  CurrencyEuroIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  CpuChipIcon,
  KeyIcon
} from '@heroicons/react/24/outline';
import { metricsApi } from '../services/api';
import { useAuthStore } from '../store/authStore';

const Dashboard: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await metricsApi.getDashboard();
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  const stats = [
    {
      name: 'Monthly Revenue',
      value: `€${metrics?.revenue_metrics.mrr.toLocaleString() || '0'}`,
      change: `${metrics?.revenue_metrics.growth_rate || 0}%`,
      changeType: (metrics?.revenue_metrics.growth_rate || 0) > 0 ? 'increase' : 'decrease',
      icon: CurrencyEuroIcon,
    },
    {
      name: 'Active Agents',
      value: metrics?.weekly_active_agents.active_agent_count || 0,
      change: '+12%',
      changeType: 'increase',
      icon: ChartBarIcon,
    },
    {
      name: 'Total Conversations',
      value: metrics?.weekly_active_agents.total_conversations || 0,
      change: '+23%',
      changeType: 'increase',
      icon: ChatBubbleBottomCenterTextIcon,
    },
    {
      name: 'Activation Rate',
      value: `${metrics?.activation_metrics.activation_rate || 0}%`,
      change: '+4%',
      changeType: 'increase',
      icon: UserGroupIcon,
    },
  ];
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">
          Welcome back, {user?.company_name}!
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Here's what's happening with your AI agents today.
        </p>
      </div>
      
      {/* Stats */}
      <dl className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-lg bg-white px-4 pb-12 pt-5 shadow sm:px-6 sm:pt-6"
          >
            <dt>
              <div className="absolute rounded-md bg-primary-500 p-3">
                <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-gray-500">
                {stat.name}
              </p>
            </dt>
            <dd className="ml-16 flex items-baseline pb-6 sm:pb-7">
              <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              <p
                className={`ml-2 flex items-baseline text-sm font-semibold ${
                  stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {stat.changeType === 'increase' ? (
                  <ArrowUpIcon className="h-5 w-5 flex-shrink-0 self-center text-green-500" />
                ) : (
                  <ArrowDownIcon className="h-5 w-5 flex-shrink-0 self-center text-red-500" />
                )}
                <span className="sr-only">
                  {stat.changeType === 'increase' ? 'Increased' : 'Decreased'} by
                </span>
                {stat.change}
              </p>
            </dd>
          </div>
        ))}
      </dl>
      
      {/* Quick Actions */}
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/agents"
          className="relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400"
        >
          <div className="flex-shrink-0">
            <CpuChipIcon className="h-10 w-10 text-primary-600" />
          </div>
          <div className="min-w-0 flex-1">
            <span className="absolute inset-0" aria-hidden="true" />
            <p className="text-sm font-medium text-gray-900">Create New Agent</p>
            <p className="truncate text-sm text-gray-500">
              Deploy a new AI agent for your website
            </p>
          </div>
        </Link>
        
        <Link
          to="/api-keys"
          className="relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400"
        >
          <div className="flex-shrink-0">
            <KeyIcon className="h-10 w-10 text-primary-600" />
          </div>
          <div className="min-w-0 flex-1">
            <span className="absolute inset-0" aria-hidden="true" />
            <p className="text-sm font-medium text-gray-900">Manage API Keys</p>
            <p className="truncate text-sm text-gray-500">
              Create keys for WordPress integration
            </p>
          </div>
        </Link>
        
        <a
          href="https://docs.netvexa.com"
          target="_blank"
          rel="noopener noreferrer"
          className="relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm hover:border-gray-400"
        >
          <div className="flex-shrink-0">
            <svg className="h-10 w-10 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div className="min-w-0 flex-1">
            <span className="absolute inset-0" aria-hidden="true" />
            <p className="text-sm font-medium text-gray-900">Documentation</p>
            <p className="truncate text-sm text-gray-500">
              Learn how to get the most from NETVEXA
            </p>
          </div>
        </a>
      </div>
      
      {/* Active Agents Table */}
      {metrics?.weekly_active_agents.agents && metrics.weekly_active_agents.agents.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Active Agents This Week</h2>
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Agent Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Conversations
                  </th>
                  <th className="relative px-6 py-3">
                    <span className="sr-only">View</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {metrics.weekly_active_agents.agents.map((agent) => (
                  <tr key={agent.agent_id}>
                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900">
                      {agent.agent_name}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                      {agent.conversation_count}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-right text-sm font-medium">
                      <Link
                        to={`/agents/${agent.agent_id}`}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;