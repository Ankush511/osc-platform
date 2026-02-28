'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import {
  getConfiguration,
  updateConfiguration,
  type ConfigurationSettings,
} from '@/lib/admin-api';

export default function ConfigurationManagement() {
  const router = useRouter();
  const { status } = useSession();
  const [config, setConfig] = useState<ConfigurationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [claimTimeoutEasy, setClaimTimeoutEasy] = useState(7);
  const [claimTimeoutMedium, setClaimTimeoutMedium] = useState(14);
  const [claimTimeoutHard, setClaimTimeoutHard] = useState(21);
  const [claimGracePeriod, setClaimGracePeriod] = useState(24);
  const [emailEnabled, setEmailEnabled] = useState(false);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
      return;
    }

    if (status === 'authenticated') {
      loadConfiguration();
    }
  }, [status, router]);

  const loadConfiguration = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getConfiguration();
      setConfig(data);
      
      // Set form values
      setClaimTimeoutEasy(data.claim_timeout_easy_days);
      setClaimTimeoutMedium(data.claim_timeout_medium_days);
      setClaimTimeoutHard(data.claim_timeout_hard_days);
      setClaimGracePeriod(data.claim_grace_period_hours);
      setEmailEnabled(data.email_enabled);
    } catch (err: any) {
      console.error('Error loading configuration:', err);
      if (err.response?.status === 403) {
        setError('You do not have admin privileges.');
      } else {
        setError('Failed to load configuration.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);

      const updates = {
        claim_timeout_easy_days: claimTimeoutEasy,
        claim_timeout_medium_days: claimTimeoutMedium,
        claim_timeout_hard_days: claimTimeoutHard,
        claim_grace_period_hours: claimGracePeriod,
        email_enabled: emailEnabled,
      };

      const updatedConfig = await updateConfiguration(updates);
      setConfig(updatedConfig);
      setSuccessMessage('Configuration updated successfully! Note: Changes are runtime only.');
    } catch (err: any) {
      setError('Failed to update configuration.');
    } finally {
      setSaving(false);
    }
  };

  if (error && !config) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={() => router.push('/admin')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Return to Admin Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/admin')}
            className="text-blue-600 hover:text-blue-800 mb-2"
          >
            ← Back to Admin Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Configuration Management</h1>
          <p className="mt-2 text-gray-600">Manage platform settings and configuration</p>
        </div>

        {loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading configuration...</p>
          </div>
        ) : (
          <>
            {/* Success Message */}
            {successMessage && (
              <div className="mb-6 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                {successMessage}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* System Information */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">System Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Environment</p>
                  <p className="font-semibold text-gray-900">{config?.environment}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">GitHub Client ID</p>
                  <p className="font-semibold text-gray-900">{config?.github_client_id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">OpenAI Configured</p>
                  <p className="font-semibold text-gray-900">
                    {config?.openai_configured ? 'Yes' : 'No'}
                  </p>
                </div>
              </div>
            </div>

            {/* Claim Timeout Settings */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Claim Timeout Settings</h2>
              <p className="text-sm text-gray-600 mb-4">
                Configure how long users can claim issues based on difficulty level.
              </p>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Easy Issues (days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={claimTimeoutEasy}
                    onChange={(e) => setClaimTimeoutEasy(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Medium Issues (days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={claimTimeoutMedium}
                    onChange={(e) => setClaimTimeoutMedium(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hard Issues (days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={claimTimeoutHard}
                    onChange={(e) => setClaimTimeoutHard(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Grace Period (hours)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="168"
                    value={claimGracePeriod}
                    onChange={(e) => setClaimGracePeriod(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Grace period before auto-releasing expired claims
                  </p>
                </div>
              </div>
            </div>

            {/* Email Settings */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Email Settings</h2>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="emailEnabled"
                  checked={emailEnabled}
                  onChange={(e) => setEmailEnabled(e.target.checked)}
                  className="mr-3"
                />
                <label htmlFor="emailEnabled" className="text-sm font-medium text-gray-700">
                  Enable email notifications
                </label>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Note: SMTP settings must be configured in environment variables
              </p>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>

            {/* Warning */}
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded p-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> Configuration changes are applied at runtime only. For persistent
                changes across restarts, update the environment variables in your deployment.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
