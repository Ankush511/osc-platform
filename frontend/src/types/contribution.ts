export type ContributionStatus = 'submitted' | 'merged' | 'closed'

export interface Contribution {
  id: number
  user_id: number
  issue_id: number
  pr_url: string
  pr_number: number
  status: ContributionStatus
  submitted_at: string
  merged_at: string | null
  points_earned: number
  issue_title?: string | null
  repository_name?: string | null
}

export interface SubmitPRRequest {
  issue_id: number
  pr_url: string
  user_id: number
}

export interface SubmissionResult {
  success: boolean
  message: string
  contribution_id?: number
  pr_number?: number
  status?: string
  points_earned?: number
}

export interface ContributionStats {
  total_contributions: number
  submitted_prs: number
  merged_prs: number
  closed_prs: number
  total_points: number
  contributions_by_language: Record<string, number>
  contributions_by_repository: Record<string, number>
}
