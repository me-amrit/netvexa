import React, { useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface DeleteAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  agentName: string;
  conversationCount: number;
  documentCount: number;
  isLoading: boolean;
}

const DeleteAgentModal: React.FC<DeleteAgentModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  agentName,
  conversationCount,
  documentCount,
  isLoading
}) => {
  const [confirmationName, setConfirmationName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (confirmationName.trim() !== agentName) {
      setError(`Please type "${agentName}" exactly to confirm deletion.`);
      return;
    }
    
    setError('');
    onConfirm();
  };

  const handleClose = () => {
    setConfirmationName('');
    setError('');
    onClose();
  };

  const isValid = confirmationName.trim() === agentName;

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-center mb-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                    <ExclamationTriangleIcon className="h-6 w-6 text-red-600" aria-hidden="true" />
                  </div>
                  <div className="ml-4">
                    <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                      Delete Agent
                    </Dialog.Title>
                    <p className="text-sm text-gray-500">
                      This action cannot be undone
                    </p>
                  </div>
                </div>

                <div className="mb-6">
                  <p className="text-sm text-gray-700 mb-4">
                    You are about to permanently delete the agent <strong>"{agentName}"</strong>.
                  </p>
                  
                  <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                    <h4 className="text-sm font-medium text-red-800 mb-2">
                      This will permanently delete:
                    </h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      <li>• The agent and its configuration</li>
                      <li>• {conversationCount} conversation{conversationCount !== 1 ? 's' : ''} and all messages</li>
                      <li>• {documentCount} knowledge document{documentCount !== 1 ? 's' : ''}</li>
                      <li>• All analytics and history data</li>
                      <li>• Any embedded widgets will stop working</li>
                    </ul>
                  </div>

                  <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                      <label htmlFor="confirmation" className="block text-sm font-medium text-gray-700 mb-2">
                        Please type <span className="font-semibold text-red-600">"{agentName}"</span> to confirm deletion:
                      </label>
                      <input
                        type="text"
                        id="confirmation"
                        value={confirmationName}
                        onChange={(e) => {
                          setConfirmationName(e.target.value);
                          setError('');
                        }}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 sm:text-sm ${
                          error 
                            ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
                            : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
                        }`}
                        placeholder={`Type "${agentName}" here`}
                        disabled={isLoading}
                      />
                      {error && (
                        <p className="mt-2 text-sm text-red-600">{error}</p>
                      )}
                    </div>

                    <div className="flex justify-end space-x-3">
                      <button
                        type="button"
                        className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                        onClick={handleClose}
                        disabled={isLoading}
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={!isValid || isLoading}
                        className="inline-flex justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isLoading ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Deleting...
                          </>
                        ) : (
                          'Delete Agent'
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default DeleteAgentModal;