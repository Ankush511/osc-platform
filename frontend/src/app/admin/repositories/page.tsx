'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import {
  getRepositories,
  addRepository,
  updateRepository,
  deleteRepository,
  triggerSync,
  type RepositoryManagement,
  type SyncResult,
} from '@/lib/admin-api';

export default function RepositoriesManagement() {
  const router = useRouter();
  const { status } = useSession();
  const [repositories, setRepositories] = useState<RepositoryManagement[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newRepoName, setNewRepoName] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
      return;
    }

    if (status === 'authenticated') {
      loadRepositories();
    }
  }, [status, page, router]);

  const loadRepositories = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRepositories({ page, page_size: 20 });
      setRepositories(data.repositories);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      console.error('Error loading repositories:', err);
      if (err.response?.status === 403) {
        setError('You do not have admin privileges.');
      } else {
        setError('Failed to load repositories.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddRepository = async () => {
    if (!newRepoName.trim()) return;

    try {
      await addRepository(newRepoName);
      setShowAddModal(false);
      setNewRepoName('');
      loadRepositories();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add repository');
    }
  };

  const handleToggleActive = async (repo: RepositoryManagement) => {
    try {
      await updateRepository(repo.id, !repo.is_active);
      loadRepositories();
    } catch (err: any) {
      alert('Failed to update repository');
    }
  };

  const handleDelete = async (repo: RepositoryManagement) {
    if (!confirm(`Are you sure you want to delete ${repo.full_name}? This will remove all associated issues.`)) {
      return;
    }

    try {
      await deleteRepository(repo.id);
      loadRepositories();
    } catch (err: any) {
      alert('Failed to delete repository');
    }
  };

  const handleSync = async (repoId?: number) => {
    try {
      setSyncing(true);
      setSyncResult(null);
      const result = await triggerSync(repoId ? [repoId] : undefined);
      setSyncResult(result);
      loadRepositories();
    } catch (err: any) {
      alert('Failed to sync repositories');
    } finally {
      setSyncing(false);
    }
  };

  if (error) {
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <button
              onClick={() => router.push('/admin')}
              className="text-blue-600 hover:text-blue-800 mb-2"
            >
              ← Back to Admin Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Repository Management</h1>
            <p className="mt-2 text-gray-600">Add, remove, and manage repositories</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleSync()}
              disabled={syncing}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              {syncing ? 'Syncing...' : 'Sync All'}
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Add Repository
            </button>
          </div>
        </div>

        {/* Sync Result */}
        {syncResult && (
          <div className="mb-6 bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Sync Results</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Repositories</p>
                <p className="font-semibold">{syncResult.repositories_synced}</p>
              </div>
              <div>
                <p className="text-gray-600">Added</p>
                <p className="font-semibold text-green-600">{syncResult.issues_added}</p>
              </div>
              <div>
                <p className="text-gray-600">Updated</p>
                <p className="font-semibold text-blue-600">{syncResult.issues_updated}</p>
              </div>
              <div>
                <p className="text-gray-600">Closed</p>
                <p className="font-semibold text-red-600">{syncResult.issues_closed}</p>
              </div>
              <div>
                <p className="text-gray-600">Duration</p>
                <p className="font-semibold">{syncResult.sync_duration_seconds.toFixed(2)}s</p>
              </div>
            </div>
            {syncResult.errors.length > 0 && (
              <div className="mt-4">
                <p className="text-red-600 font-semibold">Errors:</p>
                <ul className="list-disc list-inside text-sm text-red-600">
                  {syncResult.errors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Repositories Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading repositories...</p>
            </div>
          ) : repositories.length === 0 ? (
            <div className="p-8 text-center text-gray-600">
              No repositories found. Add one to get started.
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Repository
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Language
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Issues
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Stars
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Last Synced
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {repositories.map((repo) => (
                  <tr key={repo.id}>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{repo.full_name}</p>
                        <p className="text-sm text-gray-500">{repo.description}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {repo.primary_language || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{repo.issue_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{repo.stars}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          repo.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {repo.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {repo.last_synced
                        ? new Date(repo.last_synced).toLocaleDateString()
                        : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-right text-sm space-x-2">
                      <button
                        onClick={() => handleSync(repo.id)}
                        disabled={syncing}
                        className="text-blue-600 hover:text-blue-800 disabled:text-gray-400"
                      >
                        Sync
                      </button>
                      <button
                        onClick={() => handleToggleActive(repo)}
                        className="text-yellow-600 hover:text-yellow-800"
                      >
                        {repo.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      <button
                        onClick={() => handleDelete(repo)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 bg-white border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}

        {/* Add Repository Modal */}
        {showAddModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Add Repository</h2>
              <input
                type="text"
                value={newRepoName}
                onChange={(e) => setNewRepoName(e.target.value)}
                placeholder="owner/repository"
                className="w-full px-4 py-2 border rounded mb-4"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleAddRepository}
                  className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                  Add
                </button>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setNewRepoName('');
                  }}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
