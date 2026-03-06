import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  submitPullRequest,
  getUserContributions,
  getUserContributionStats,
  getContributionById,
} from '../contributions-api'
import * as apiClient from '../api-client'

vi.mock('../api-client')

describe('contributions-api', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('submitPullRequest', () => {
    it('submits PR with correct parameters', async () => {
      const mockResult = {
        success: true,
        message: 'PR submitted successfully',
        contribution_id: 1,
        pr_number: 123,
        status: 'submitted',
        points_earned: 10,
      }

      vi.mocked(apiClient.api.post).mockResolvedValue(mockResult)

      const result = await submitPullRequest(
        456,
        'https://github.com/owner/repo/pull/123',
        789,
        'test-token'
      )

      expect(apiClient.api.post).toHaveBeenCalledWith(
        '/api/v1/contributions/submit',
        {
          issue_id: 456,
          pr_url: 'https://github.com/owner/repo/pull/123',
          user_id: 789,
        },
        'test-token'
      )

      expect(result).toEqual(mockResult)
    })

    it('handles submission errors', async () => {
      vi.mocked(apiClient.api.post).mockRejectedValue(
        new Error('PR validation failed')
      )

      await expect(
        submitPullRequest(456, 'https://github.com/owner/repo/pull/123', 789, 'test-token')
      ).rejects.toThrow('PR validation failed')
    })
  })

  describe('getUserContributions', () => {
    it('fetches user contributions without status filter', async () => {
      const mockContributions = [
        {
          id: 1,
          user_id: 123,
          issue_id: 456,
          pr_url: 'https://github.com/owner/repo/pull/789',
          pr_number: 789,
          status: 'submitted',
          submitted_at: '2024-01-15T10:00:00Z',
          merged_at: null,
          points_earned: 10,
        },
      ]

      vi.mocked(apiClient.api.get).mockResolvedValue(mockContributions)

      const result = await getUserContributions(123, 'test-token')

      expect(apiClient.api.get).toHaveBeenCalledWith(
        '/api/v1/contributions/user/123',
        'test-token'
      )

      expect(result).toEqual(mockContributions)
    })

    it('fetches user contributions with status filter', async () => {
      const mockContributions = [
        {
          id: 1,
          user_id: 123,
          issue_id: 456,
          pr_url: 'https://github.com/owner/repo/pull/789',
          pr_number: 789,
          status: 'merged',
          submitted_at: '2024-01-15T10:00:00Z',
          merged_at: '2024-01-16T14:30:00Z',
          points_earned: 100,
        },
      ]

      vi.mocked(apiClient.api.get).mockResolvedValue(mockContributions)

      const result = await getUserContributions(123, 'test-token', 'merged')

      expect(apiClient.api.get).toHaveBeenCalledWith(
        '/api/v1/contributions/user/123?status=merged',
        'test-token'
      )

      expect(result).toEqual(mockContributions)
    })

    it('handles fetch errors', async () => {
      vi.mocked(apiClient.api.get).mockRejectedValue(
        new Error('Failed to fetch contributions')
      )

      await expect(
        getUserContributions(123, 'test-token')
      ).rejects.toThrow('Failed to fetch contributions')
    })
  })

  describe('getUserContributionStats', () => {
    it('fetches user contribution statistics', async () => {
      const mockStats = {
        total_contributions: 5,
        submitted_prs: 2,
        merged_prs: 3,
        closed_prs: 0,
        total_points: 310,
        contributions_by_language: {
          TypeScript: 3,
          Python: 2,
        },
        contributions_by_repository: {
          'owner/repo1': 3,
          'owner/repo2': 2,
        },
      }

      vi.mocked(apiClient.api.get).mockResolvedValue(mockStats)

      const result = await getUserContributionStats(123, 'test-token')

      expect(apiClient.api.get).toHaveBeenCalledWith(
        '/api/v1/contributions/user/123/stats',
        'test-token'
      )

      expect(result).toEqual(mockStats)
    })

    it('handles stats fetch errors', async () => {
      vi.mocked(apiClient.api.get).mockRejectedValue(
        new Error('Failed to fetch stats')
      )

      await expect(
        getUserContributionStats(123, 'test-token')
      ).rejects.toThrow('Failed to fetch stats')
    })
  })

  describe('getContributionById', () => {
    it('fetches specific contribution by ID', async () => {
      const mockContribution = {
        id: 1,
        user_id: 123,
        issue_id: 456,
        pr_url: 'https://github.com/owner/repo/pull/789',
        pr_number: 789,
        status: 'submitted',
        submitted_at: '2024-01-15T10:00:00Z',
        merged_at: null,
        points_earned: 10,
      }

      vi.mocked(apiClient.api.get).mockResolvedValue(mockContribution)

      const result = await getContributionById(1, 'test-token')

      expect(apiClient.api.get).toHaveBeenCalledWith(
        '/api/v1/contributions/1',
        'test-token'
      )

      expect(result).toEqual(mockContribution)
    })

    it('handles contribution not found', async () => {
      vi.mocked(apiClient.api.get).mockRejectedValue(
        new Error('Contribution not found')
      )

      await expect(
        getContributionById(999, 'test-token')
      ).rejects.toThrow('Contribution not found')
    })
  })
})
