import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { useAuthStore } from '../store/authStore';
import { userApi } from '../services/api';
import { 
  UserCircleIcon, 
  KeyIcon, 
  BellIcon,
  CreditCardIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface SettingsForm {
  companyName: string;
  email: string;
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
  emailNotifications: boolean;
  marketingEmails: boolean;
}

const Settings: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'notifications' | 'billing'>('profile');
  
  const { register, handleSubmit, watch, reset, formState: { errors } } = useForm<SettingsForm>({
    defaultValues: {
      companyName: user?.company_name || '',
      email: user?.email || '',
      emailNotifications: true,
      marketingEmails: false,
    },
  });
  
  const newPassword = watch('newPassword');
  
  const updateProfileMutation = useMutation({
    mutationFn: (data: { company_name: string; email: string }) => 
      userApi.updateProfile(data),
    onSuccess: () => {
      toast.success('Profile updated successfully');
    },
    onError: () => {
      toast.error('Failed to update profile');
    },
  });
  
  const updatePasswordMutation = useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) => 
      userApi.updatePassword(data),
    onSuccess: () => {
      toast.success('Password updated successfully');
      reset({ currentPassword: '', newPassword: '', confirmPassword: '' });
    },
    onError: () => {
      toast.error('Failed to update password. Please check your current password.');
    },
  });
  
  const handleProfileSubmit = (data: SettingsForm) => {
    updateProfileMutation.mutate({
      company_name: data.companyName,
      email: data.email,
    });
  };
  
  const handlePasswordSubmit = (data: SettingsForm) => {
    if (!data.currentPassword || !data.newPassword) {
      toast.error('Please fill in all password fields');
      return;
    }
    
    updatePasswordMutation.mutate({
      current_password: data.currentPassword,
      new_password: data.newPassword,
    });
  };
  
  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'password', name: 'Password & Security', icon: KeyIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'billing', name: 'Billing', icon: CreditCardIcon },
  ];
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account settings and preferences
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  group relative min-w-0 flex-1 overflow-hidden py-4 px-4 text-center text-sm font-medium 
                  ${activeTab === tab.id
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700 border-b-2 border-transparent'
                  }
                `}
              >
                <tab.icon className="mx-auto h-6 w-6 mb-1" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
        
        <div className="p-6">
          {activeTab === 'profile' && (
            <form onSubmit={handleSubmit(handleProfileSubmit)} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium leading-6 text-gray-900">Profile Information</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Update your company information and email address.
                </p>
              </div>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="companyName" className="block text-sm font-medium text-gray-700">
                    Company Name
                  </label>
                  <input
                    {...register('companyName', { 
                      required: 'Company name is required',
                      minLength: { value: 2, message: 'Company name must be at least 2 characters' }
                    })}
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  {errors.companyName && (
                    <p className="mt-1 text-sm text-red-600">{errors.companyName.message}</p>
                  )}
                </div>
                
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email Address
                  </label>
                  <input
                    {...register('email', { 
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    type="email"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
                  )}
                </div>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={updateProfileMutation.isPending}
                  className="inline-flex justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  {updateProfileMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}
          
          {activeTab === 'password' && (
            <form onSubmit={handleSubmit(handlePasswordSubmit)} className="space-y-6">
              <div>
                <h3 className="text-lg font-medium leading-6 text-gray-900">Password & Security</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Ensure your account stays secure by using a strong password.
                </p>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700">
                    Current Password
                  </label>
                  <input
                    {...register('currentPassword')}
                    type="password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
                
                <div>
                  <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                    New Password
                  </label>
                  <input
                    {...register('newPassword', {
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters'
                      },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
                        message: 'Password must contain uppercase, lowercase, number and special character'
                      }
                    })}
                    type="password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  {errors.newPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.newPassword.message}</p>
                  )}
                </div>
                
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                    Confirm New Password
                  </label>
                  <input
                    {...register('confirmPassword', {
                      validate: value => value === newPassword || 'Passwords do not match'
                    })}
                    type="password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>
              
              <div className="rounded-md bg-blue-50 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <ShieldCheckIcon className="h-5 w-5 text-blue-400" aria-hidden="true" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">Password Requirements</h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <ul className="list-disc list-inside space-y-1">
                        <li>At least 8 characters long</li>
                        <li>Include uppercase and lowercase letters</li>
                        <li>Include at least one number</li>
                        <li>Include at least one special character</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={updatePasswordMutation.isPending}
                  className="inline-flex justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  {updatePasswordMutation.isPending ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </form>
          )}
          
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium leading-6 text-gray-900">Email Notifications</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Manage how you receive notifications from NETVEXA.
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="flex h-5 items-center">
                    <input
                      {...register('emailNotifications')}
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="emailNotifications" className="text-sm font-medium text-gray-700">
                      Email notifications
                    </label>
                    <p className="text-sm text-gray-500">
                      Receive email notifications about important account activity
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex h-5 items-center">
                    <input
                      {...register('marketingEmails')}
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                  </div>
                  <div className="ml-3">
                    <label htmlFor="marketingEmails" className="text-sm font-medium text-gray-700">
                      Marketing emails
                    </label>
                    <p className="text-sm text-gray-500">
                      Receive emails about new features, tips, and special offers
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  className="inline-flex justify-center rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                  Save Preferences
                </button>
              </div>
            </div>
          )}
          
          {activeTab === 'billing' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium leading-6 text-gray-900">Billing & Subscription</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Manage your subscription and billing information.
                </p>
              </div>
              
              <div className="rounded-md bg-gray-50 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Free Plan</h4>
                    <p className="mt-1 text-sm text-gray-500">You're currently on the free plan</p>
                  </div>
                  <button className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500">
                    Upgrade to Pro
                  </button>
                </div>
                
                <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Current Usage</p>
                    <p className="mt-1 text-2xl font-semibold text-gray-900">1,234</p>
                    <p className="text-sm text-gray-500">messages this month</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Plan Limit</p>
                    <p className="mt-1 text-2xl font-semibold text-gray-900">5,000</p>
                    <p className="text-sm text-gray-500">messages per month</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Next Reset</p>
                    <p className="mt-1 text-2xl font-semibold text-gray-900">15</p>
                    <p className="text-sm text-gray-500">days remaining</p>
                  </div>
                </div>
              </div>
              
              <div className="border-t border-gray-200 pt-6">
                <h4 className="text-sm font-medium text-gray-900">Payment Method</h4>
                <p className="mt-1 text-sm text-gray-500">No payment method on file</p>
                <button className="mt-4 text-sm text-primary-600 hover:text-primary-500">
                  Add payment method
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;