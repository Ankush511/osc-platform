export type DifficultyLevel = 'easy' | 'medium' | 'hard' | 'unknown'

export interface LearningResource {
  title: string
  url: string
  type: string
  description?: string
}

export interface RepositorySummaryResponse {
  repository_id: number
  summary: string
  cached: boolean
}

export interface IssueExplanationResponse {
  issue_id: number
  explanation: string
  difficulty_level: DifficultyLevel
  learning_resources: LearningResource[]
  cached: boolean
}

export interface ClaimResult {
  success: boolean
  message: string
  issue_id?: number
  claimed_at?: string
  claim_expires_at?: string
}

export interface ReleaseResult {
  success: boolean
  message: string
  issue_id?: number
}

export interface ExtensionResult {
  success: boolean
  message: string
  issue_id?: number
  new_expiration?: string
}
