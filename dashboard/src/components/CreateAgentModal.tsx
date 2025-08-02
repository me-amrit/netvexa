import React, { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { useForm } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { agentApi } from '../services/api';

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CreateAgentForm {
  name: string;
  tone: string;
  language: string;
  responseStyle: string;
  welcomeMessage: string;
}

const CreateAgentModal: React.FC<CreateAgentModalProps> = ({ isOpen, onClose }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, reset, formState: { errors } } = useForm<CreateAgentForm>({
    defaultValues: {
      tone: 'professional',
      language: 'en',
      responseStyle: 'concise',
      welcomeMessage: 'Hello! How can I help you today?',
    },
  });
  
  const createMutation = useMutation({
    mutationFn: (data: CreateAgentForm) => 
      agentApi.create({
        name: data.name,
        personality: {
          tone: data.tone,
          language: data.language,
          response_style: data.responseStyle,
        },
        welcome_message: data.welcomeMessage,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      toast.success('Agent created successfully');
      handleClose();
    },
    onError: () => {
      toast.error('Failed to create agent');
    },
  });
  
  const handleClose = () => {
    reset();
    onClose();
  };
  
  const onSubmit = (data: CreateAgentForm) => {
    createMutation.mutate(data);
  };
  
  return (
    <Transition.Root show={isOpen} as={Fragment}>
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
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div className="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                    onClick={handleClose}
                  >
                    <span className="sr-only">Close</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
                
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-gray-900">
                      Create New Agent
                    </Dialog.Title>
                    
                    <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
                      <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                          Agent Name
                        </label>
                        <input
                          {...register('name', { 
                            required: 'Agent name is required',
                            minLength: { value: 3, message: 'Name must be at least 3 characters' }
                          })}
                          type="text"
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                          placeholder="Customer Support Agent"
                        />
                        {errors.name && (
                          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                        )}
                      </div>
                      
                      <div>
                        <label htmlFor="tone" className="block text-sm font-medium text-gray-700">
                          Personality Tone
                        </label>
                        <select
                          {...register('tone')}
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
                          {...register('language')}
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
                          {...register('responseStyle')}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                        >
                          <option value="concise">Concise</option>
                          <option value="detailed">Detailed</option>
                          <option value="conversational">Conversational</option>
                        </select>
                      </div>
                      
                      <div>
                        <label htmlFor="welcomeMessage" className="block text-sm font-medium text-gray-700">
                          Welcome Message
                        </label>
                        <textarea
                          {...register('welcomeMessage', { 
                            required: 'Welcome message is required',
                            maxLength: { value: 500, message: 'Message must be less than 500 characters' }
                          })}
                          rows={3}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                          placeholder="Hello! I'm here to help you with any questions about our products and services."
                        />
                        {errors.welcomeMessage && (
                          <p className="mt-1 text-sm text-red-600">{errors.welcomeMessage.message}</p>
                        )}
                      </div>
                      
                      <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                        <button
                          type="submit"
                          disabled={createMutation.isPending}
                          className="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 sm:ml-3 sm:w-auto disabled:opacity-50"
                        >
                          {createMutation.isPending ? 'Creating...' : 'Create Agent'}
                        </button>
                        <button
                          type="button"
                          className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                          onClick={handleClose}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};

export default CreateAgentModal;