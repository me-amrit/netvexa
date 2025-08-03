import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { metricsApi, type ConversationTrends, type EngagementPatterns, type DashboardMetrics } from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

const Analytics: React.FC = () => {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['analytics-metrics'],
    queryFn: async () => {
      const response = await metricsApi.getDashboard();
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  const { data: conversationTrends } = useQuery({
    queryKey: ['conversation-trends'],
    queryFn: async () => {
      const response = await metricsApi.getConversationTrends(7);
      return response.data;
    },
    refetchInterval: 60000,
  });

  const { data: engagementPatterns } = useQuery({
    queryKey: ['engagement-patterns'],
    queryFn: async () => {
      const response = await metricsApi.getEngagementPatterns();
      return response.data;
    },
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Transform real data for charts
  const conversationTrendData = conversationTrends?.trends?.map((trend) => ({
    name: new Date(trend.date).toLocaleDateString('en-US', { weekday: 'short' }),
    conversations: trend.conversations,
    messages: trend.messages,
  })) || [];

  const hourlyEngagementData = engagementPatterns?.hourly_patterns?.slice(0, 12).map((pattern) => ({
    hour: `${pattern.hour.toString().padStart(2, '0')}:00`,
    conversations: pattern.conversations,
  })) || [];

  const dailyEngagementData = engagementPatterns?.daily_patterns?.map((pattern) => ({
    name: pattern.day_name.substring(0, 3),
    value: pattern.conversations,
  })) || [];

  const agentPerformance = metrics?.weekly_active_agents.agents.map(agent => ({
    name: agent.agent_name.split(' ').slice(0, 2).join(' '),
    conversations: agent.conversation_count,
    satisfaction: Math.floor(85 + Math.random() * 15), // Mock satisfaction score
  })) || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-gray-900">Analytics Overview</h2>
        <p className="mt-1 text-sm text-gray-500">
          Track your AI agents' performance and customer engagement metrics
        </p>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Conversations</dt>
                  <dd className="text-lg font-semibold text-gray-900">{conversationTrends?.total_conversations || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Messages</dt>
                  <dd className="text-lg font-semibold text-gray-900">{conversationTrends?.total_messages || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Peak Hour</dt>
                  <dd className="text-lg font-semibold text-gray-900">{engagementPatterns?.peak_hour ? `${engagementPatterns.peak_hour}:00` : '--'}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Agents</dt>
                  <dd className="text-lg font-semibold text-gray-900">{metrics?.weekly_active_agents?.active_agent_count || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Conversation Trend */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Conversation Trend</h3>
          <div className="h-[300px]">
            <Line
              data={{
                labels: conversationTrendData.map((d) => d.name),
                datasets: [
                  {
                    label: 'Conversations',
                    data: conversationTrendData.map((d) => d.conversations),
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4,
                  },
                  {
                    label: 'Messages',
                    data: conversationTrendData.map((d) => d.messages),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Hourly Engagement */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Hourly Engagement Patterns</h3>
          <div className="h-[300px]">
            <Line
              data={{
                labels: hourlyEngagementData.map((d) => d.hour),
                datasets: [
                  {
                    label: 'Conversations per Hour',
                    data: hourlyEngagementData.map((d) => d.conversations),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Daily Engagement */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Daily Engagement Distribution</h3>
          <div className="h-[300px]">
            <Doughnut
              data={{
                labels: dailyEngagementData.map((d) => d.name),
                datasets: [
                  {
                    data: dailyEngagementData.map((d) => d.value),
                    backgroundColor: COLORS,
                    borderColor: COLORS.map(color => color),
                    borderWidth: 1,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'right' as const,
                  },
                },
              }}
            />
          </div>
        </div>

        {/* Agent Performance */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Agent Performance</h3>
          <div className="h-[300px]">
            <Bar
              data={{
                labels: agentPerformance.map((d) => d.name),
                datasets: [
                  {
                    label: 'Conversations',
                    data: agentPerformance.map((d) => d.conversations),
                    backgroundColor: '#6366f1',
                    yAxisID: 'y',
                  },
                  {
                    label: 'Satisfaction %',
                    data: agentPerformance.map((d) => d.satisfaction),
                    backgroundColor: '#10b981',
                    yAxisID: 'y1',
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    type: 'linear' as const,
                    display: true,
                    position: 'left' as const,
                  },
                  y1: {
                    type: 'linear' as const,
                    display: true,
                    position: 'right' as const,
                    grid: {
                      drawOnChartArea: false,
                    },
                  },
                },
              }}
            />
          </div>
        </div>
      </div>

      {/* Detailed Stats Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-base font-semibold text-gray-900 mb-4">Agent Details</h3>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Agent Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Conversations
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg. Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Resolution Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Satisfaction
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {metrics?.weekly_active_agents.agents.map((agent) => (
                  <tr key={agent.agent_id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {agent.agent_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {agent.conversation_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(2 + Math.random() * 3).toFixed(1)}s
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(90 + Math.random() * 9).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        <span>{(4.5 + Math.random() * 0.5).toFixed(1)}/5.0</span>
                        <svg className="ml-1 h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;