import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ArrowLeftIcon, 
  DocumentTextIcon, 
  ChatBubbleLeftRightIcon,
  CogIcon,
  PlusIcon,
  TrashIcon,
  PaperClipIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { agentApi, conversationApi } from '../services/api';
import ConversationHistory from '../components/ConversationHistory';

interface Document {
  id: string;
  name: string;
  size: number;
  uploaded_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

const AgentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'test' | 'conversations' | 'documents' | 'settings'>('test');
  const [testMessage, setTestMessage] = useState('');
  const [testConversation, setTestConversation] = useState<Message[]>([]);
  const [isTestLoading, setIsTestLoading] = useState(false);
  
  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', id],
    queryFn: async () => {
      const response = await agentApi.get(id!);
      return response.data;
    },
    enabled: !!id,
  });
  
  const { data: conversations } = useQuery({
    queryKey: ['agent-conversations', id],
    queryFn: async () => {
      const response = await conversationApi.list(id!);
      return response.data;
    },
    enabled: !!id,
  });
  
  const updateMutation = useMutation({
    mutationFn: (data: any) => agentApi.update(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent', id] });
      toast.success('Agent updated successfully');
    },
    onError: () => {
      toast.error('Failed to update agent');
    },
  });
  
  const handleTestMessage = async () => {
    if (!testMessage.trim()) return;
    
    setIsTestLoading(true);
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: testMessage,
      timestamp: new Date().toISOString(),
    };
    
    setTestConversation(prev => [...prev, userMessage]);
    setTestMessage('');
    
    try {
      const response = await agentApi.testMessage(id!, { message: testMessage });
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
      };
      setTestConversation(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Failed to send test message');
      setTestConversation(prev => prev.slice(0, -1));
    } finally {
      setIsTestLoading(false);
    }
  };
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await agentApi.uploadDocument(id!, formData);
      queryClient.invalidateQueries({ queryKey: ['agent', id] });
      toast.success('Document uploaded successfully');
    } catch (error) {
      toast.error('Failed to upload document');
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  if (!agent) {
    return <div>Agent not found</div>;
  }
  
  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/agents"
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back to Agents
        </Link>
        
        <div className="mt-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{agent.name}</h1>
            <p className="mt-1 text-sm text-gray-500">
              Created {new Date(agent.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
              {agent.status || 'Active'}
            </span>
            <span className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
              {agent.config.personality.tone}
            </span>
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('test')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'test'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ChatBubbleLeftRightIcon className="inline-block h-5 w-5 mr-2" />
            Test Chat
          </button>
          <button
            onClick={() => setActiveTab('conversations')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'conversations'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ClockIcon className="inline-block h-5 w-5 mr-2" />
            History ({agent.conversation_count || 0})
          </button>
          <button
            onClick={() => setActiveTab('documents')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'documents'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <DocumentTextIcon className="inline-block h-5 w-5 mr-2" />
            Documents ({agent.document_count || 0})
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'settings'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <CogIcon className="inline-block h-5 w-5 mr-2" />
            Settings
          </button>
        </nav>
      </div>
      
      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'test' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Test Chat */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Test Conversation</h3>
              <div className="bg-white rounded-lg shadow">
                <div className="h-96 overflow-y-auto p-4 space-y-4">
                  {testConversation.length === 0 ? (
                    <div className="text-center text-gray-500 mt-8">
                      <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <p className="mt-2">Start a test conversation</p>
                    </div>
                  ) : (
                    testConversation.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs px-4 py-2 rounded-lg ${
                            message.role === 'user'
                              ? 'bg-primary-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className="text-xs mt-1 opacity-70">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                  {isTestLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-4 py-2 rounded-lg">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="border-t p-4">
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      handleTestMessage();
                    }}
                    className="flex space-x-2"
                  >
                    <input
                      type="text"
                      value={testMessage}
                      onChange={(e) => setTestMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      disabled={isTestLoading}
                    />
                    <button
                      type="submit"
                      disabled={isTestLoading || !testMessage.trim()}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                    >
                      Send
                    </button>
                  </form>
                </div>
              </div>
            </div>
            
            {/* Recent Conversations */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Conversations</h3>
              <div className="bg-white shadow rounded-lg">
                {conversations && conversations.length > 0 ? (
                  <ul className="divide-y divide-gray-200">
                    {conversations.slice(0, 5).map((conversation: any) => (
                      <li key={conversation.id} className="p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">
                              {conversation.user_identifier || 'Anonymous User'}
                            </p>
                            <p className="text-sm text-gray-500">
                              {conversation.message_count} messages
                            </p>
                          </div>
                          <time className="text-sm text-gray-500">
                            {conversation.started_at ? new Date(conversation.started_at).toLocaleDateString() : 'Unknown date'}
                          </time>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm text-gray-500">No conversations yet</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'conversations' && (
          <ConversationHistory agentId={id!} />
        )}
        
        {activeTab === 'documents' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Knowledge Base Documents</h3>
              <label className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 cursor-pointer">
                <PlusIcon className="h-5 w-5 mr-2" />
                Upload Document
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={handleFileUpload}
                />
              </label>
            </div>
            
            {agent.documents && agent.documents.length > 0 ? (
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                  {agent.documents.map((doc: Document) => (
                    <li key={doc.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <PaperClipIcon className="h-5 w-5 text-gray-400 mr-3" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                            <p className="text-sm text-gray-500">
                              {(doc.size / 1024).toFixed(2)} KB • Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <button className="text-red-600 hover:text-red-900">
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No documents</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Upload documents to enhance your agent's knowledge
                </p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Agent Settings</h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                updateMutation.mutate({
                  name: formData.get('name'),
                  personality: {
                    tone: formData.get('tone'),
                    language: formData.get('language'),
                    response_style: formData.get('responseStyle'),
                  },
                  welcome_message: formData.get('welcomeMessage'),
                });
              }}
              className="space-y-6"
            >
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                  Agent Name
                </label>
                <input
                  type="text"
                  name="name"
                  defaultValue={agent.name}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                <div>
                  <label htmlFor="tone" className="block text-sm font-medium text-gray-700">
                    Personality Tone
                  </label>
                  <select
                    name="tone"
                    defaultValue={agent.config.personality.tone}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  >
                    <option value="professional">Professional</option>
                    <option value="friendly">Friendly</option>
                    <option value="casual">Casual</option>
                    <option value="formal">Formal</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="language" className="block text-sm font-medium text-gray-700">
                    Language
                  </label>
                  <select
                    name="language"
                    defaultValue={agent.config.personality.language}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  >
                    <option value="en">English</option>
                    <option value="de">German</option>
                    <option value="fr">French</option>
                    <option value="es">Spanish</option>
                    <option value="it">Italian</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="responseStyle" className="block text-sm font-medium text-gray-700">
                    Response Style
                  </label>
                  <select
                    name="responseStyle"
                    defaultValue={agent.config.personality.response_style}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  >
                    <option value="concise">Concise</option>
                    <option value="detailed">Detailed</option>
                    <option value="conversational">Conversational</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label htmlFor="welcomeMessage" className="block text-sm font-medium text-gray-700">
                  Welcome Message
                </label>
                <textarea
                  name="welcomeMessage"
                  rows={3}
                  defaultValue={agent.config.welcome_message}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentDetail;