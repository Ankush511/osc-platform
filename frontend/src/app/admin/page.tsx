'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import {
  getPlatformStats,
  checkSystemHealth,
  getRateLimitStatus,
  type PlatformStats,
  type SystemHealth,
  type RateLimitStatus,
} from '@/lib/admin-api';

export default function AdminDashboard() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [rateLimit, setRateLimit] = useState<RateLimitStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
      return;
    }

    if (status === 'authenticated') {
      loadDashboardData();
    }
  }, [status, router]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statsData, healthData, rateLimitData] = await Promise.all([
        getPlatformStats(),
        checkSystemHealth(),
        getRateLimitStatus(),
      ]);

      setStats(statsData);
      setHealth(healthData);
      setRateLimit(rateLimitData);
    } catch (err: any) {
      console.error('Error loading admin dashboard:', err);
      if (err.response?.status === 403) {
        setError('You do not have admin privileges to access this page.');
      } else {
        setError('Failed to load dashboard data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'configured':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="mt-2 text-gray-600">Platform management and monitoring</p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <button
            onClick={() => router.push('/admin/repositories')}
            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-gray-900">Repositories</h3>
            <p className="text-sm text-gray-600">Manage repositories</p>
          </button>
          <button
            onClick={() => router.push('/admin/users')}
            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-gray-900">Users</h3>
            <p className="text-sm text-gray-600">Manage users</p>
          </button>
          <button
            onClick={() => router.push('/admin/config')}
            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <h3 className="font-semibold text-gray-900">Configuration</h3>
            <p className="text-sm text-gray-600">Platform settings</p>
          </button>
          <button
            onClick={loadDashboardData}
            className="bg-blue-600 text-white p-4 rounded-lg shadow hover:bg-blue-700 transition-colors"
          >
            <h3 className="font-semibold">Refresh</h3>
            <p className="text-sm">Reload data</p>
          </button>
        </div>

        {/* Platform Statistics */}
        {stats && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Platform Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <StatCard title="Total Users" value={stats.total_users} />
              <StatCard title="Active Users (30d)" value={stats.active_users_last_30_days} />
              <StatCard title="Total Repositories" value={stats.total_repositories} />
              <StatCard title="Active Repositories" value={stats.active_repositories} />
              <StatCard title="Total Issues" value={stats.total_issues} />
              <StatCard title="Available Issues" value={stats.available_issues} />
              <StatCard title="Claimed Issues" value={stats.claimed_issues} />
              <StatCard title="Completed Issues" value={stats.completed_issues} />
              <StatCard title="Total Contributions" value={stats.total_contributions} />
              <StatCard title="Merged PRs" value={stats.merged_prs} />
              <StatCard title="Pending PRs" value={stats.pending_prs} />
            </div>
          </div>
        )}

        {/* System Health */}
        {health && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">System Health</h2>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center mb-6">
                <span className="text-lg font-semibold mr-3">Overall Status:</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(
                    health.status
                  )}`}
                >
                  {health.status.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <HealthComponent name="Database" component={health.database} />
                <HealthComponent name="Redis" component={health.redis} />
                <HealthComponent name="GitHub API" component={health.github_api} />
                <HealthComponent name="AI Service" component={health.ai_service} />
                <HealthComponent name="Celery" component={health.celery} />
              </div>
            </div>
          </div>
        )}

        {/* GitHub Rate Limit */}
        {rateLimit && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">GitHub API Rate Limit</h2>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Remaining</p>
                  <p className="text-2xl font-bold text-gray-900">{rateLimit.remaining}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Limit</p>
                  <p className="text-2xl font-bold text-gray-900">{rateLimit.limit}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Used</p>
                  <p className="text-2xl font-bold text-gray-900">{rateLimit.used}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Usage</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {rateLimit.percentage_used.toFixed(1)}%
                  </p>
                </div>
              </div>
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      rateLimit.percentage_used > 80
                        ? 'bg-red-600'
                        : rateLimit.percentage_used > 50
                        ? 'bg-yellow-600'
                        : 'bg-green-600'
                    }`}
                    style={{ width: `${rateLimit.percentage_used}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Resets at: {new Date(rateLimit.reset_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function HealthComponent({
  name,
  component,
}: {
  name: string;
  component: { status: string; details: Record<string, any> };
}) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'configured':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'unhealthy':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h3 className="font-semibold text-gray-900 mb-2">{name}</h3>
      <p className={`text-sm font-medium ${getStatusColor(component.status)}`}>
        {component.status.toUpperCase()}
      </p>
      {Object.keys(component.details).length > 0 && (
        <div className="mt-2 text-xs text-gray-600">
          {Object.entries(component.details).map(([key, value]) => (
            <div key={key}>
              <span className="font-medium">{key}:</span> {String(value)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
