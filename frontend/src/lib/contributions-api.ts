import { api } from './api-client'
import {
  Contribution,
  SubmitPRRequest,
  SubmissionResult,
  ContributionStats,
} from '@/types/contribution'

/**
 * Submit a pull request for validation
 */
export async function submitPullRequest(
  issueId: number,
  prUrl: string,
  userId: number,
  token: string
): Promise<SubmissionResult> {
  const request: SubmitPRRequest = {
    issue_id: issueId,
    pr_url: prUrl,
    user_id: userId,
  }

  return api.post<SubmissionResult>('/api/v1/contributions/submit', request, token)
}

/**
 * Get all contributions for a user
 */
export async function getUserContributions(
  userId: number,
  token: string,
  status?: string
): Promise<Contribution[]> {
  const params = status ? `?status=${status}` : ''
  return api.get<Contribution[]>(`/api/v1/contributions/user/${userId}${params}`, token)
}

/**
 * Get contribution statistics for a user
 */
export async function getUserContributionStats(
  userId: number,
  token: string
): Promise<ContributionStats> {
  return api.get<ContributionStats>(`/api/v1/contributions/user/${userId}/stats`, token)
}

/**
 * Get a specific contribution by ID
 */
export async function getContributionById(
  contributionId: number,
  token: string
): Promise<Contribution> {
  return api.get<Contribution>(`/api/v1/contributions/${contributionId}`, token)
}
