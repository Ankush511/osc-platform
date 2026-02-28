import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import PRManagement from '../PRManagement'
import * as contributionsApi from '@/lib/contributions-api'
import { Contribution } from '@/types/contribution'

vi.mock('@/lib/contributions-api')

describe('PRManagement', () => {
  const defaultProps = {
    userId: 123,
    issueId: 456,
    accessToken: 'test-token',
  }

  const mockContribution: Contribution = {
    id: 1,
    user_id: 123,
    issue_id: 456,
    pr_url: 'https://github.com/owner/repo/pull/789',
    pr_number: 789,
    status: 'submitted',
    submitted_at: '2024-01-15T10:00:00Z',
    merged_at: null,
    points_earned: 10,
    issue_title: 'Fix bug in authentication',
    repository_name: 'owner/repo',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state initially', () => {
    vi.mocked(contributionsApi.getUserContributions).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<PRManagement {...defaultProps} />)

    // Check for loading spinner SVG
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('loads and displays contribution for the issue', async () => {
    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([mockContribution])

    render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText(/your contribution/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/pending review/i)).toBeInTheDocument()
    expect(screen.getByText(/PR #789/i)).toBeInTheDocument()
  })

  it('does not display anything when no contribution exists', async () => {
    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([])

    const { container } = render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(contributionsApi.getUserContributions).toHaveBeenCalled()
    })

    // Component should render nothing
    expect(container.firstChild).toBeNull()
  })

  it('displays error message on API failure', async () => {
    vi.mocked(contributionsApi.getUserContributions).mockRejectedValue(
      new Error('Failed to load contributions')
    )

    render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText(/failed to load contribution/i)).toBeInTheDocument()
    })
  })

  it('allows retry after error', async () => {
    vi.mocked(contributionsApi.getUserContributions)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce([mockContribution])

    render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument()
    })

    const retryButton = screen.getByRole('button', { name: /retry/i })
    retryButton.click()

    await waitFor(() => {
      expect(screen.getByText(/your contribution/i)).toBeInTheDocument()
    })
  })

  it('filters contributions by issue ID', async () => {
    const otherContribution: Contribution = {
      ...mockContribution,
      id: 2,
      issue_id: 999,
    }

    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([
      mockContribution,
      otherContribution,
    ])

    render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(screen.getByText(/your contribution/i)).toBeInTheDocument()
    })

    // Should only display the contribution for issue 456
    expect(screen.getByText(/PR #789/i)).toBeInTheDocument()
  })

  it('calls API with correct parameters', async () => {
    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([mockContribution])

    render(<PRManagement {...defaultProps} />)

    await waitFor(() => {
      expect(contributionsApi.getUserContributions).toHaveBeenCalledWith(123, 'test-token')
    })
  })
})
