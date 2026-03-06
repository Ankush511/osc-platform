import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getCurrentUser,
  updateUserPreferences,
  getUserStats,
  getUserAchievements,
} from '../users-api'

global.fetch = vi.fn()

describe('users-api', () => {
  const mockAccessToken = 'test-access-token'
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getCurrentUser', () => {
    it('fetches current user profile successfully', async () => {
      const mockUser = {
        id: 1,
        github_username: 'testuser',
        github_id: 12345,
        email: 'test@example.com',
        avatar_url: 'https://example.com/avatar.jpg',
        full_name: 'Test User',
        bio: 'Test bio',
        location: 'Test Location',
        preferred_languages: ['Python', 'JavaScript'],
        preferred_labels: ['bug', 'enhancement'],
        total_contributions: 10,
        merged_prs: 5,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-15T00:00:00Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      })

      const result = await getCurrentUser(mockAccessToken)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/users/me`,
        expect.objectContaining({
          headers: {
            'Authorization': `Bearer ${mockAccessToken}`,
          },
          cache: 'no-store',
        })
      )
      expect(result).toEqual(mockUser)
    })

    it('throws error when fetch fails', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
      })

      await expect(getCurrentUser(mockAccessToken)).rejects.toThrow(
        'Failed to fetch user profile'
      )
    })
  })

  describe('updateUserPreferences', () => {
    it('updates user preferences successfully', async () => {
      const preferences = {
        preferred_languages: ['Python', 'TypeScript'],
        preferred_labels: ['good first issue'],
      }

      const mockResponse = {
        id: 1,
        github_username: 'testuser',
        preferred_languages: ['Python', 'TypeScript'],
        preferred_labels: ['good first issue'],
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await updateUserPreferences(preferences, mockAccessToken)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/users/me/preferences`,
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${mockAccessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(preferences),
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('throws error when update fails', async () => {
      const preferences = {
        preferred_languages: ['Python'],
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
      })

      await expect(
        updateUserPreferences(preferences, mockAccessToken)
      ).rejects.toThrow('Failed to update preferences')
    })
  })

  describe('getUserStats', () => {
    it('fetches user stats successfully', async () => {
      const mockStats = {
        user_id: 1,
        total_contributions: 10,
        total_prs_submitted: 8,
        merged_prs: 5,
        contributions_by_language: { Python: 5, JavaScript: 3 },
        contributions_by_repo: { 'owner/repo': 5 },
        recent_contributions: [],
        calculated_at: '2024-01-15T00:00:00Z',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats,
      })

      const result = await getUserStats(mockAccessToken)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/users/me/stats`,
        expect.objectContaining({
          headers: {
            'Authorization': `Bearer ${mockAccessToken}`,
          },
          cache: 'no-store',
        })
      )
      expect(result).toEqual(mockStats)
    })

    it('throws error when fetch fails', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      await expect(getUserStats(mockAccessToken)).rejects.toThrow(
        'Failed to fetch user stats'
      )
    })
  })

  describe('getUserAchievements', () => {
    it('fetches user achievements successfully', async () => {
      const mockAchievements = [
        {
          achievement: {
            id: 1,
            name: 'First Contribution',
            description: 'Submit your first PR',
            badge_icon: '🎉',
            category: 'milestone',
            threshold: 1,
            created_at: '2024-01-01T00:00:00Z',
          },
          progress: 1,
          is_unlocked: true,
          earned_at: '2024-01-15T00:00:00Z',
          percentage: 100,
        },
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockAchievements,
      })

      const result = await getUserAchievements(mockAccessToken)

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_URL}/api/v1/users/me/achievements`,
        expect.objectContaining({
          headers: {
            'Authorization': `Bearer ${mockAccessToken}`,
          },
          cache: 'no-store',
        })
      )
      expect(result).toEqual(mockAchievements)
    })

    it('throws error when fetch fails', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      })

      await expect(getUserAchievements(mockAccessToken)).rejects.toThrow(
        'Failed to fetch user achievements'
      )
    })
  })
})
