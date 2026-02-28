export interface UserStats {
  user_id: number
  total_contributions: number
  total_prs_submitted: number
  merged_prs: number
  contributions_by_language: Record<string, number>
  contributions_by_repo: Record<string, number>
  recent_contributions: RecentContribution[]
  calculated_at: string
}

export interface RecentContribution {
  contribution_id: number
  issue_title: string
  repository: string
  status: 'submitted' | 'merged' | 'closed'
  pr_url: string
  submitted_at: string
  merged_at: string | null
}

export interface Achievement {
  id: number
  name: string
  description: string
  badge_icon: string
  category: string
  threshold: number
  created_at: string
}

export interface UserAchievementProgress {
  achievement: Achievement
  progress: number
  is_unlocked: boolean
  earned_at: string | null
  percentage: number
}

export interface AchievementStats {
  total_achievements: number
  unlocked_achievements: number
  completion_percentage: number
}

export interface DashboardData {
  user: {
    id: number
    github_username: string
    avatar_url: string
    full_name: string | null
    bio: string | null
    total_contributions: number
    merged_prs: number
    preferred_languages: string[]
    preferred_labels: string[]
  }
  statistics: UserStats
  achievements: UserAchievementProgress[]
  achievement_stats: AchievementStats
}
