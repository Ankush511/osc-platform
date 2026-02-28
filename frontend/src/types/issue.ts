export type IssueStatus = 'available' | 'claimed' | 'completed' | 'closed'
export type DifficultyLevel = 'easy' | 'medium' | 'hard' | 'unknown'

export interface Issue {
  id: number
  github_issue_id: number
  repository_id: number
  title: string
  description: string | null
  labels: string[]
  programming_language: string | null
  difficulty_level: string | null
  ai_explanation: string | null
  status: IssueStatus
  claimed_by: number | null
  claimed_at: string | null
  claim_expires_at: string | null
  github_url: string
  created_at: string
  updated_at: string
  repository_name: string | null
  repository_full_name: string | null
}

export interface IssueFilters {
  programming_languages?: string[]
  labels?: string[]
  difficulty_levels?: string[]
  status?: IssueStatus
  search_query?: string
  repository_id?: number
}

export interface PaginatedIssuesResponse {
  items: Issue[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AvailableFilters {
  programming_languages: string[]
  labels: string[]
  difficulty_levels: string[]
}
