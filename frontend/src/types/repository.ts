export interface Repository {
  id: number
  github_repo_id: number
  full_name: string
  name: string
  description: string | null
  primary_language: string | null
  topics: string[]
  stars: number
  forks: number
  ai_summary: string | null
  is_active: boolean
  last_synced: string | null
  created_at: string
}
