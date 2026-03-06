import { RepositorySummaryResponse, IssueExplanationResponse } from '@/types/ai'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchRepositorySummary(
  repositoryId: number,
  accessToken: string,
  forceRegenerate: boolean = false
): Promise<RepositorySummaryResponse> {
  const response = await fetch(`${API_URL}/api/v1/ai/repository-summary`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      repository_id: repositoryId,
      force_regenerate: forceRegenerate,
    }),
    cache: 'no-store',
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail?.message || 'Failed to fetch repository summary')
  }
  
  return response.json()
}

export async function fetchIssueExplanation(
  issueId: number,
  accessToken: string,
  forceRegenerate: boolean = false
): Promise<IssueExplanationResponse> {
  const response = await fetch(`${API_URL}/api/v1/ai/issue-explanation`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      issue_id: issueId,
      force_regenerate: forceRegenerate,
    }),
    cache: 'no-store',
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail?.message || 'Failed to fetch issue explanation')
  }
  
  return response.json()
}
