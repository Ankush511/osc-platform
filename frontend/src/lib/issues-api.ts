import { Issue, IssueFilters, PaginatedIssuesResponse, AvailableFilters } from '@/types/issue'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface FetchIssuesParams {
  page?: number
  page_size?: number
  filters?: IssueFilters
  accessToken?: string
}

export async function fetchIssues({
  page = 1,
  page_size = 20,
  filters = {},
  accessToken,
}: FetchIssuesParams): Promise<PaginatedIssuesResponse> {
  const params = new URLSearchParams()
  
  params.append('page', page.toString())
  params.append('page_size', page_size.toString())
  
  if (filters.programming_languages?.length) {
    params.append('programming_languages', filters.programming_languages.join(','))
  }
  
  if (filters.labels?.length) {
    params.append('labels', filters.labels.join(','))
  }
  
  if (filters.difficulty_levels?.length) {
    params.append('difficulty_levels', filters.difficulty_levels.join(','))
  }
  
  if (filters.status) {
    params.append('status', filters.status)
  }
  
  if (filters.search_query) {
    params.append('search_query', filters.search_query)
  }
  
  if (filters.repository_id) {
    params.append('repository_id', filters.repository_id.toString())
  }

  const headers: Record<string, string> = {}
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }
  
  const response = await fetch(`${API_URL}/api/v1/issues/?${params.toString()}`, {
    headers,
    cache: 'no-store',
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch issues: ${response.statusText}`)
  }
  
  return response.json()
}

export async function fetchAvailableFilters(accessToken?: string): Promise<AvailableFilters> {
  const headers: Record<string, string> = {}
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`

  const response = await fetch(`${API_URL}/api/v1/issues/filters/available`, {
    headers,
    cache: 'no-store',
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch available filters: ${response.statusText}`)
  }
  
  return response.json()
}

export async function fetchIssueById(issueId: number, accessToken: string): Promise<Issue> {
  const response = await fetch(`${API_URL}/api/v1/issues/${issueId}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch issue: ${response.statusText}`)
  }
  
  return response.json()
}

export async function claimIssue(issueId: number, accessToken: string) {
  const response = await fetch(`${API_URL}/api/v1/issues/${issueId}/claim`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to claim issue')
  }
  
  return response.json()
}

export async function releaseIssue(issueId: number, accessToken: string, reason?: string) {
  const response = await fetch(`${API_URL}/api/v1/issues/${issueId}/release`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason: reason || undefined }),
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to release issue')
  }
  
  return response.json()
}

export async function extendClaimDeadline(
  issueId: number,
  extensionDays: number,
  justification: string,
  accessToken: string
) {
  const response = await fetch(`${API_URL}/api/v1/issues/${issueId}/extend`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      extension_days: extensionDays,
      justification,
    }),
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to extend deadline' }))
    throw new Error(error.detail || error.message || 'Failed to extend deadline')
  }
  
  return response.json()
}

export async function submitPullRequest(issueId: number, prUrl: string, accessToken: string) {
  const response = await fetch(`${API_URL}/api/v1/contributions/submit`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ issue_id: issueId, pr_url: prUrl }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to submit PR' }))
    throw new Error(error.detail || error.message || 'Failed to submit PR')
  }

  return response.json()
}

export async function simulatePR(issueId: number, simulateMerge: boolean, accessToken: string) {
  const response = await fetch(`${API_URL}/api/v1/contributions/dev/simulate-pr`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ issue_id: issueId, simulate_merge: simulateMerge }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to simulate PR' }))
    throw new Error(error.detail || error.message || 'Failed to simulate PR')
  }

  return response.json()
}
