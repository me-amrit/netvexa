import axios from 'axios';

// Set base URL from environment variable or default to localhost
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Types
export interface Agent {
  id: string;
  name: string;
  config: {
    personality: {
      tone: string;
      language: string;
      response_style: string;
    };
    welcome_message: string;
    is_active: boolean;
  };
  created_at: string;
  updated_at: string;
  conversation_count?: number;
  document_count?: number;
  status?: string;
  documents?: Document[];
}

export interface Document {
  id: string;
  name: string;
  size: number;
  uploaded_at: string;
}

export interface CreateAgentData {
  name: string;
  personality?: {
    tone: string;
    language: string;
    response_style: string;
  };
  welcome_message?: string;
}

export interface ApiKey {
  id: string;
  name: string;
  key?: string; // Only present when creating
  key_preview: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
  usage_count: number;
}

export interface Conversation {
  id: string;
  agent_id: string;
  started_at: string;
  ended_at?: string;
  message_count: number;
  lead_captured: boolean;
}

export interface Message {
  id: number;
  conversation_id: string;
  sender: 'user' | 'agent';
  content: string;
  timestamp: string;
}

export interface DashboardMetrics {
  weekly_active_agents: {
    active_agent_count: number;
    total_conversations: number;
    agents: Array<{
      agent_id: string;
      agent_name: string;
      conversation_count: number;
    }>;
  };
  activation_metrics: {
    trial_users: number;
    converted_users: number;
    activation_rate: number;
  };
  revenue_metrics: {
    mrr: number;
    arr: number;
    arpu: number;
    growth_rate: number;
  };
}

export interface ConversationTrends {
  trends: Array<{
    date: string;
    conversations: number;
    messages: number;
  }>;
  total_conversations: number;
  total_messages: number;
  period_days: number;
}

export interface EngagementPatterns {
  hourly_patterns: Array<{
    hour: number;
    conversations: number;
  }>;
  daily_patterns: Array<{
    day: number;
    day_name: string;
    conversations: number;
  }>;
  peak_hour: number;
  peak_day: string;
}

// Agent API
export const agentApi = {
  list: () => axios.get<Agent[]>('/api/agents/'),
  
  get: (id: string) => axios.get<Agent>(`/api/agents/${id}`),
  
  create: (data: CreateAgentData) => axios.post<Agent>('/api/agents/', data),
  
  update: (id: string, data: Partial<CreateAgentData>) => 
    axios.put<Agent>(`/api/agents/${id}`, data),
  
  delete: (id: string) => axios.delete(`/api/agents/${id}`),
  
  testMessage: (id: string, data: { message: string }) => 
    axios.post<{ response: string }>(`/api/agents/${id}/test-message?message=${encodeURIComponent(data.message)}`, {}),
    
  uploadDocument: (id: string, formData: FormData) => {
    formData.append('agent_id', id);
    return axios.post('/api/knowledge/ingest/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// API Key Management
export const apiKeyApi = {
  list: () => axios.get<ApiKey[]>('/api/auth/api-keys'),
  
  create: (data: { name: string }) => 
    axios.post<ApiKey>('/api/auth/api-keys', data),
  
  delete: (id: string) => axios.delete(`/api/auth/api-keys/${id}`),
};

// Knowledge Management
export const knowledgeApi = {
  ingestUrl: (agentId: string, url: string) => 
    axios.post('/api/knowledge/ingest-url', { agent_id: agentId, url }),
  
  ingestText: (agentId: string, text: string, metadata?: any) => 
    axios.post('/api/knowledge/ingest-text', { 
      agent_id: agentId, 
      text, 
      metadata 
    }),
    
  getDocuments: (agentId: string) => 
    axios.get(`/api/agents/${agentId}/documents`),
};

// Conversation History
export const conversationApi = {
  list: (agentId: string) => 
    axios.get<Conversation[]>(`/api/agents/${agentId}/conversations`),
  
  get: (conversationId: string) => 
    axios.get<Message[]>(`/api/conversations/${conversationId}/messages`),
};

// Metrics API
export const metricsApi = {
  getDashboard: () => 
    axios.get<DashboardMetrics>('/api/metrics/dashboard'),
  
  getAgentMetrics: (agentId: string) => 
    axios.get(`/api/metrics/agents/${agentId}/time-to-value`),
  
  getConversationQuality: (conversationId: string) => 
    axios.get(`/api/metrics/conversations/${conversationId}/quality`),
  
  getConversationTrends: (days: number = 7) => 
    axios.get<ConversationTrends>(`/api/metrics/conversations/trends?days=${days}`),
  
  getAgentPerformance: (agentId: string, days: number = 30) => 
    axios.get(`/api/metrics/agents/${agentId}/performance?days=${days}`),
  
  getEngagementPatterns: () => 
    axios.get<EngagementPatterns>('/api/metrics/engagement/patterns'),
};

// User API
export const userApi = {
  updateProfile: (data: { company_name: string; email: string }) => 
    axios.put('/api/auth/profile', data),
    
  updatePassword: (data: { current_password: string; new_password: string }) => 
    axios.put('/api/auth/password', data),
};