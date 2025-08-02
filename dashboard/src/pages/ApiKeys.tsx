import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  PlusIcon, 
  TrashIcon, 
  EyeIcon, 
  EyeSlashIcon,
  ClipboardDocumentIcon,
  ExclamationTriangleIcon,
  KeyIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { apiKeyApi } from '../services/api';

interface ApiKey {
  id: string;
  name: string;
  key_preview: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
  usage_count: number;
}

interface CreateApiKeyResponse {
  id: string;
  name: string;
  key: string;
  key_preview: string;
}

const ApiKeys: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [createdKey, setCreatedKey] = useState<CreateApiKeyResponse | null>(null);
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
  const queryClient = useQueryClient();
  
  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ['api-keys'],
    queryFn: async () => {
      const response = await apiKeyApi.list();
      return response.data;
    },
  });
  
  const createMutation = useMutation({
    mutationFn: (name: string) => apiKeyApi.create({ name }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      setCreatedKey(response.data as CreateApiKeyResponse);
      setNewKeyName('');
      toast.success('API key created successfully');
    },
    onError: () => {
      toast.error('Failed to create API key');
    },
  });
  
  const deleteMutation = useMutation({
    mutationFn: apiKeyApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
      toast.success('API key deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete API key');
    },
  });
  
  const handleCreate = () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a name for the API key');
      return;
    }
    createMutation.mutate(newKeyName);
  };
  
  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete the API key "${name}"? This action cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };
  
  const toggleKeyVisibility = (keyId: string) => {
    setVisibleKeys(prev => {
      const newSet = new Set(prev);
      if (newSet.has(keyId)) {
        newSet.delete(keyId);
      } else {
        newSet.add(keyId);
      }
      return newSet;
    });
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  
  const hasApiKeys = apiKeys && apiKeys.length > 0;
  const activeKeys = apiKeys?.filter(key => key.is_active) || [];
  
  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">API Keys</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage API keys for WordPress plugin integration. Keep your keys secure and never share them publicly.
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            type="button"
            onClick={() => setIsCreateModalOpen(true)}
            disabled={activeKeys.length >= 5}
            className="block rounded-md bg-primary-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlusIcon className="inline-block h-5 w-5 mr-1 -mt-1" />
            Create API Key
          </button>
          {activeKeys.length >= 5 && (
            <p className="mt-1 text-xs text-red-600">Maximum API keys reached (5)</p>
          )}
        </div>
      </div>
      
      {/* Security Warning */}
      <div className="mt-6 rounded-md bg-yellow-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" aria-hidden="true" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Security Notice</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                API keys provide full access to your NETVEXA account. Keep them secure and never share them in public repositories or client-side code.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {!hasApiKeys ? (
        <div className="mt-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No API keys</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new API key for your WordPress integration.</p>
          <div className="mt-6">
            <button
              type="button"
              onClick={() => setIsCreateModalOpen(true)}
              className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
            >
              <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
              Create API Key
            </button>
          </div>
        </div>
      ) : (
        <div className="mt-8 overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:-mx-6 md:mx-0 md:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  Name
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  API Key
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Usage
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Last Used
                </th>
                <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Created
                </th>
                <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {apiKeys.map((apiKey) => (
                <tr key={apiKey.id} className={!apiKey.is_active ? 'opacity-50' : ''}>
                  <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    {apiKey.name}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-2">
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                        {visibleKeys.has(apiKey.id) ? `${apiKey.key_preview}...` : '••••••••'}
                      </code>
                      <button
                        onClick={() => toggleKeyVisibility(apiKey.id)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        {visibleKeys.has(apiKey.id) ? (
                          <EyeSlashIcon className="h-4 w-4" />
                        ) : (
                          <EyeIcon className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {apiKey.is_active ? (
                      <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {apiKey.usage_count} requests
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {apiKey.last_used_at ? new Date(apiKey.last_used_at).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {new Date(apiKey.created_at).toLocaleDateString()}
                  </td>
                  <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    {apiKey.is_active && (
                      <button
                        onClick={() => handleDelete(apiKey.id, apiKey.name)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="inline-block h-5 w-5" />
                        <span className="sr-only">Delete {apiKey.name}</span>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Create API Key Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setIsCreateModalOpen(false)} />
            
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <h3 className="text-lg font-semibold leading-6 text-gray-900">Create API Key</h3>
                <div className="mt-4">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Key Name
                  </label>
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="WordPress Production"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    A descriptive name to help you identify this key
                  </p>
                </div>
              </div>
              <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button
                  type="button"
                  onClick={handleCreate}
                  disabled={createMutation.isPending}
                  className="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 sm:col-start-2 disabled:opacity-50"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsCreateModalOpen(false);
                    setNewKeyName('');
                  }}
                  className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* New API Key Display Modal */}
      {createdKey && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
            
            <div className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                  <KeyIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
                </div>
                <div className="mt-3 text-center sm:mt-5">
                  <h3 className="text-lg font-semibold leading-6 text-gray-900">API Key Created</h3>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">
                      Your API key has been created. This is the only time you'll see the full key. Please copy it now and store it securely.
                    </p>
                  </div>
                  <div className="mt-4">
                    <div className="rounded-md bg-gray-50 p-4">
                      <code className="text-sm break-all">{createdKey.key}</code>
                    </div>
                    <button
                      onClick={() => copyToClipboard(createdKey.key)}
                      className="mt-2 inline-flex items-center text-sm text-primary-600 hover:text-primary-500"
                    >
                      <ClipboardDocumentIcon className="h-5 w-5 mr-1" />
                      Copy to clipboard
                    </button>
                  </div>
                </div>
              </div>
              <div className="mt-5 sm:mt-6">
                <button
                  type="button"
                  onClick={() => setCreatedKey(null)}
                  className="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiKeys;