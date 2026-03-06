const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface UserPreferences {
  preferred_languages?: string[]
  preferred_labels?: string[]
}

export interface UserProfile {
  id: number
  github_username: string
  github_id: number
  email: string | null
  avatar_url: string
  full_name: string | null
  bio: string | null
  location: string | null
  preferred_languages: string[]
  preferred_labels: string[]
  total_contributions: number
  merged_prs: number
  created_at: string
  updated_at: string
}

export async function getCurrentUser(accessToken: string): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/api/v1/users/me`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user profile')
  }

  return response.json()
}

export async function updateUserPreferences(
  preferences: UserPreferences,
  accessToken: string
): Promise<UserProfile> {
  const response = await fetch(`${API_URL}/api/v1/users/me/preferences`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(preferences),
  })

  if (!response.ok) {
    throw new Error('Failed to update preferences')
  }

  return response.json()
}

export async function getUserStats(accessToken: string) {
  const response = await fetch(`${API_URL}/api/v1/users/me/stats`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user stats')
  }

  return response.json()
}

export async function getUserAchievements(accessToken: string) {
  const response = await fetch(`${API_URL}/api/v1/users/me/achievements`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    throw new Error('Failed to fetch user achievements')
  }

  return response.json()
}
