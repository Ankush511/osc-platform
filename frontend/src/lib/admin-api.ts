/**
 * Admin API client for platform management
 */
import { api } from './api-client';

// Adapter that wraps the fetch-based `api` to match the axios-style
// interface used throughout this file (response.data pattern).
const apiClient = {
  get: async <T = any>(endpoint: string, opts?: { params?: Record<string, any> }) => {
    let url = `/api/v1${endpoint}`;
    if (opts?.params) {
      const qs = new URLSearchParams();
      for (const [k, v] of Object.entries(opts.params)) {
        if (v !== undefined && v !== null) qs.append(k, String(v));
      }
      const s = qs.toString();
      if (s) url += `?${s}`;
    }
    const data = await api.get<T>(url);
    return { data };
  },
  post: async <T = any>(endpoint: string, body?: any) => {
    const data = await api.post<T>(`/api/v1${endpoint}`, body);
    return { data };
  },
  patch: async <T = any>(endpoint: string, body?: any) => {
    const data = await api.patch<T>(`/api/v1${endpoint}`, body);
    return { data };
  },
  delete: async <T = any>(endpoint: string) => {
    const data = await api.delete<T>(`/api/v1${endpoint}`);
    return { data };
  },
};

export interface PlatformStats {
  total_users: number;
  active_users_last_30_days: number;
  total_repositories: number;
  active_repositories: number;
  total_issues: number;
  available_issues: number;
  claimed_issues: number;
  completed_issues: number;
  total_contributions: number;
  merged_prs: number;
  pending_prs: number;
}

export interface RepositoryManagement {
  id: number;
  full_name: string;
  name: string;
  description: string | null;
  primary_language: string | null;
  stars: number;
  forks: number;
  is_active: boolean;
  last_synced: string | null;
  issue_count: number;
  created_at: string;
}

export interface UserManagement {
  id: number;
  github_username: string;
  email: string | null;
  full_name: string | null;
  is_admin: boolean;
  total_contributions: number;
  merged_prs: number;
  claimed_issues_count: number;
  created_at: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  database: {
    status: string;
    details: Record<string, any>;
  };
  redis: {
    status: string;
    details: Record<string, any>;
  };
  github_api: {
    status: string;
    details: Record<string, any>;
  };
  ai_service: {
    status: string;
    details: Record<string, any>;
  };
  celery: {
    status: string;
    details: Record<string, any>;
  };
  timestamp: string;
}

export interface ConfigurationSettings {
  github_client_id: string;
  openai_configured: boolean;
  email_enabled: boolean;
  claim_timeout_easy_days: number;
  claim_timeout_medium_days: number;
  claim_timeout_hard_days: number;
  claim_grace_period_hours: number;
  environment: string;
}

export interface RateLimitStatus {
  limit: number;
  remaining: number;
  reset_at: string;
  used: number;
  percentage_used: number;
}

export interface SyncResult {
  repositories_synced: number;
  issues_added: number;
  issues_updated: number;
  issues_closed: number;
  errors: string[];
  sync_duration_seconds: number;
}

/**
 * Get platform statistics
 */
export async function getPlatformStats(): Promise<PlatformStats> {
  const response = await apiClient.get('/admin/stats');
  return response.data;
}

/**
 * Get repositories with pagination
 */
export async function getRepositories(params: {
  active_only?: boolean;
  page?: number;
  page_size?: number;
}): Promise<{
  repositories: RepositoryManagement[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}> {
  const response = await apiClient.get('/admin/repositories', { params });
  return response.data;
}

/**
 * Add a new repository
 */
export async function addRepository(fullName: string): Promise<RepositoryManagement> {
  const response = await apiClient.post('/admin/repositories', {
    full_name: fullName,
  });
  return response.data;
}

/**
 * Update repository settings
 */
export async function updateRepository(
  repoId: number,
  isActive: boolean
): Promise<RepositoryManagement> {
  const response = await apiClient.patch(`/admin/repositories/${repoId}`, {
    is_active: isActive,
  });
  return response.data;
}

/**
 * Delete a repository
 */
export async function deleteRepository(repoId: number): Promise<void> {
  await apiClient.delete(`/admin/repositories/${repoId}`);
}

/**
 * Trigger repository synchronization
 */
export async function triggerSync(repositoryIds?: number[]): Promise<SyncResult> {
  const response = await apiClient.post('/admin/repositories/sync', {
    repository_ids: repositoryIds,
  });
  return response.data;
}

/**
 * Get users with pagination
 */
export async function getUsers(params: {
  page?: number;
  page_size?: number;
  admin_only?: boolean;
}): Promise<{
  users: UserManagement[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}> {
  const response = await apiClient.get('/admin/users', { params });
  return response.data;
}

/**
 * Update user role
 */
export async function updateUserRole(
  userId: number,
  isAdmin: boolean
): Promise<UserManagement> {
  const response = await apiClient.patch(`/admin/users/${userId}/role`, {
    is_admin: isAdmin,
  });
  return response.data;
}

/**
 * Check system health
 */
export async function checkSystemHealth(): Promise<SystemHealth> {
  const response = await apiClient.get('/admin/health');
  return response.data;
}

/**
 * Get configuration settings
 */
export async function getConfiguration(): Promise<ConfigurationSettings> {
  const response = await apiClient.get('/admin/config');
  return response.data;
}

/**
 * Update configuration settings
 */
export async function updateConfiguration(
  updates: Partial<{
    claim_timeout_easy_days: number;
    claim_timeout_medium_days: number;
    claim_timeout_hard_days: number;
    claim_grace_period_hours: number;
    email_enabled: boolean;
  }>
): Promise<ConfigurationSettings> {
  const response = await apiClient.patch('/admin/config', updates);
  return response.data;
}

/**
 * Get GitHub API rate limit status
 */
export async function getRateLimitStatus(): Promise<RateLimitStatus> {
  const response = await apiClient.get('/admin/rate-limit');
  return response.data;
}
