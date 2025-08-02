import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  ChatBubbleLeftRightIcon,
  CalendarIcon,
  UserIcon,
  ClockIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/outline';
import { conversationApi } from '../services/api';

interface ConversationHistoryProps {
  agentId: string;
}

interface Conversation {
  id: string;
  agent_id: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
  lead_captured: boolean;
  user_identifier?: string;
  messages?: Message[];
}

interface Message {
  id: number;
  conversation_id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({ agentId }) => {
  const [expandedConversations, setExpandedConversations] = useState<Set<string>>(new Set());
  const [selectedTimeRange, setSelectedTimeRange] = useState<'today' | 'week' | 'month' | 'all'>('week');
  
  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations', agentId, selectedTimeRange],
    queryFn: async () => {
      const response = await conversationApi.list(agentId);
      return response.data;
    },
  });
  
  const toggleConversation = async (conversationId: string) => {
    const newExpanded = new Set(expandedConversations);
    if (newExpanded.has(conversationId)) {
      newExpanded.delete(conversationId);
    } else {
      newExpanded.add(conversationId);
    }
    setExpandedConversations(newExpanded);
  };
  
  const { data: conversationMessages } = useQuery({
    queryKey: ['conversation-messages', Array.from(expandedConversations)],
    queryFn: async () => {
      const messagesMap: Record<string, Message[]> = {};
      for (const convId of expandedConversations) {
        const response = await conversationApi.get(convId);
        messagesMap[convId] = response.data;
      }
      return messagesMap;
    },
    enabled: expandedConversations.size > 0,
  });
  
  const filterConversationsByTimeRange = (conversations: Conversation[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    return conversations.filter(conv => {
      const convDate = new Date(conv.started_at);
      switch (selectedTimeRange) {
        case 'today':
          return convDate >= today;
        case 'week':
          return convDate >= weekAgo;
        case 'month':
          return convDate >= monthAgo;
        case 'all':
        default:
          return true;
      }
    });
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  const filteredConversations = conversations ? filterConversationsByTimeRange(conversations) : [];
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Conversation History</h3>
        <select
          value={selectedTimeRange}
          onChange={(e) => setSelectedTimeRange(e.target.value as any)}
          className="rounded-md border-gray-300 text-sm"
        >
          <option value="today">Today</option>
          <option value="week">Last 7 days</option>
          <option value="month">Last 30 days</option>
          <option value="all">All time</option>
        </select>
      </div>
      
      {filteredConversations.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
          <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No conversations</h3>
          <p className="mt-1 text-sm text-gray-500">
            No conversations found for the selected time range.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredConversations.map((conversation) => (
            <div
              key={conversation.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
            >
              <div
                className="px-4 py-3 cursor-pointer hover:bg-gray-50"
                onClick={() => toggleConversation(conversation.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <UserIcon className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {conversation.user_identifier || 'Anonymous User'}
                      </p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <CalendarIcon className="h-3 w-3 mr-1" />
                          {new Date(conversation.started_at).toLocaleDateString()}
                        </span>
                        <span className="flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {new Date(conversation.started_at).toLocaleTimeString()}
                        </span>
                        <span className="flex items-center">
                          <ChatBubbleLeftRightIcon className="h-3 w-3 mr-1" />
                          {conversation.message_count} messages
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {conversation.lead_captured && (
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
                        Lead Captured
                      </span>
                    )}
                    {expandedConversations.has(conversation.id) ? (
                      <ChevronUpIcon className="h-5 w-5 text-gray-400" />
                    ) : (
                      <ChevronDownIcon className="h-5 w-5 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>
              
              {expandedConversations.has(conversation.id) && (
                <div className="border-t border-gray-200 px-4 py-3 bg-gray-50">
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {conversationMessages?.[conversation.id]?.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs px-4 py-2 rounded-lg ${
                            message.sender === 'user'
                              ? 'bg-primary-600 text-white'
                              : 'bg-white text-gray-900 border border-gray-200'
                          }`}
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className={`text-xs mt-1 ${
                            message.sender === 'user' ? 'text-primary-200' : 'text-gray-500'
                          }`}>
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    )) || (
                      <div className="text-center py-4">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ConversationHistory;