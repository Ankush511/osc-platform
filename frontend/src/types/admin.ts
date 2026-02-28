/**
 * Admin-related type definitions
 */

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
  database: ComponentHealth;
  redis: ComponentHealth;
  github_api: ComponentHealth;
  ai_service: ComponentHealth;
  celery: ComponentHealth;
  timestamp: string;
}

export interface ComponentHealth {
  status: string;
  details: Record<string, any>;
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
