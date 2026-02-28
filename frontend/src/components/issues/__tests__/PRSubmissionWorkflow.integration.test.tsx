import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import IssueDetailClient from '../IssueDetailClient'
import * as contributionsApi from '@/lib/contributions-api'
import * as issuesApi from '@/lib/issues-api'
import { Issue } from '@/types/issue'

vi.mock('@/lib/contributions-api')
vi.mock('@/lib/issues-api')

describe('PR Submission Workflow Integration', () => {
  const mockIssue: Issue = {
    id: 1,
    github_issue_id: 123,
    repository_id: 456,
    title: 'Fix authentication bug',
    description: 'The login form is not validating properly',
    labels: ['bug', 'good first issue'],
    programming_language: 'TypeScript',
    difficulty_level: 'easy',
    ai_explanation: 'This issue requires fixing the validation logic',
    status: 'claimed',
    claimed_by: 789,
    claimed_at: '2024-01-15T10:00:00Z',
    claim_expires_at: '2024-01-22T10:00:00Z',
    github_url: 'https://github.com/owner/repo/issues/123',
    created_at: '2024-01-10T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    repository_name: 'repo',
    repository_full_name: 'owner/repo',
  }

  const defaultProps = {
    issue: mockIssue,
    repositorySummary: {
      repository_id: 456,
      summary: 'A great open source project',
      generated_at: '2024-01-15T10:00:00Z',
    },
    issueExplanation: {
      issue_id: 1,
      explanation: 'You need to add validation to the login form',
      learning_resources: [],
      generated_at: '2024-01-15T10:00:00Z',
    },
    accessToken: 'test-token',
    currentUserId: 789,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('completes full PR submission workflow successfully', async () => {
    const mockSubmissionResult = {
      success: true,
      message: 'PR submitted successfully',
      contribution_id: 1,
      pr_number: 999,
      status: 'submitted',
      points_earned: 10,
    }

    const mockContribution = {
      id: 1,
      user_id: 789,
      issue_id: 1,
      pr_url: 'https://github.com/owner/repo/pull/999',
      pr_number: 999,
      status: 'submitted' as const,
      submitted_at: '2024-01-16T10:00:00Z',
      merged_at: null,
      points_earned: 10,
      issue_title: 'Fix authentication bug',
      repository_name: 'owner/repo',
    }

    vi.mocked(contributionsApi.submitPullRequest).mockResolvedValue(mockSubmissionResult)
    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([mockContribution])

    render(<IssueDetailClient {...defaultProps} />)

    // Step 1: Click "Submit Pull Request" button
    const submitPRButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitPRButton)

    // Step 2: Form should appear
    await waitFor(() => {
      expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    })

    // Step 3: Enter PR URL
    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/999' } })

    // Step 4: Submit the form
    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    // Step 5: Verify API was called correctly
    await waitFor(() => {
      expect(contributionsApi.submitPullRequest).toHaveBeenCalledWith(
        1,
        'https://github.com/owner/repo/pull/999',
        789,
        'test-token'
      )
    })

    // Step 6: Celebration modal should appear
    await waitFor(() => {
      expect(screen.getByText(/pr submitted!/i)).toBeInTheDocument()
    })

    // Check for PR number in celebration (there will be multiple instances)
    const prNumbers = screen.getAllByText(/#999/i)
    expect(prNumbers.length).toBeGreaterThan(0)
    
    const points = screen.getAllByText(/\+10/i)
    expect(points.length).toBeGreaterThan(0)

    // Step 7: Close celebration
    const continueButton = screen.getByRole('button', { name: /continue/i })
    fireEvent.click(continueButton)

    // Celebration should close
    await waitFor(() => {
      expect(screen.queryByText(/pr submitted!/i)).not.toBeInTheDocument()
    })
  })

  it('handles PR submission validation errors', async () => {
    render(<IssueDetailClient {...defaultProps} />)

    // Click "Submit Pull Request" button
    const submitPRButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitPRButton)

    await waitFor(() => {
      expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    })

    // Enter invalid URL (not a GitHub URL)
    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://gitlab.com/owner/repo/merge_requests/1' } })

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    // Validation error should appear
    await waitFor(() => {
      expect(screen.getByText(/url must be from github.com/i)).toBeInTheDocument()
    })

    // API should not be called
    expect(contributionsApi.submitPullRequest).not.toHaveBeenCalled()
  })

  it('handles PR submission API errors', async () => {
    const mockErrorResult = {
      success: false,
      message: 'PR validation failed: PR not found',
    }

    vi.mocked(contributionsApi.submitPullRequest).mockResolvedValue(mockErrorResult)

    render(<IssueDetailClient {...defaultProps} />)

    // Click "Submit Pull Request" button
    const submitPRButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitPRButton)

    await waitFor(() => {
      expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    })

    // Enter valid URL
    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/999' } })

    // Submit the form
    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/pr validation failed: pr not found/i)).toBeInTheDocument()
    })

    // Celebration should not appear
    expect(screen.queryByText(/pr submitted!/i)).not.toBeInTheDocument()
  })

  it('allows canceling PR submission', async () => {
    render(<IssueDetailClient {...defaultProps} />)

    // Click "Submit Pull Request" button
    const submitPRButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitPRButton)

    await waitFor(() => {
      expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    })

    // Click cancel button in the form
    const cancelButtons = screen.getAllByRole('button', { name: /cancel/i })
    // The form cancel button should be the last one
    const formCancelButton = cancelButtons[cancelButtons.length - 1]
    fireEvent.click(formCancelButton)

    // Form should disappear
    await waitFor(() => {
      expect(screen.queryByLabelText(/pull request url/i)).not.toBeInTheDocument()
    })
  })

  it('shows PR management after successful submission', async () => {
    const mockSubmissionResult = {
      success: true,
      message: 'PR submitted successfully',
      contribution_id: 1,
      pr_number: 999,
      status: 'submitted',
      points_earned: 10,
    }

    const mockContribution = {
      id: 1,
      user_id: 789,
      issue_id: 1,
      pr_url: 'https://github.com/owner/repo/pull/999',
      pr_number: 999,
      status: 'submitted' as const,
      submitted_at: '2024-01-16T10:00:00Z',
      merged_at: null,
      points_earned: 10,
      issue_title: 'Fix authentication bug',
      repository_name: 'owner/repo',
    }

    vi.mocked(contributionsApi.submitPullRequest).mockResolvedValue(mockSubmissionResult)
    vi.mocked(contributionsApi.getUserContributions).mockResolvedValue([mockContribution])

    render(<IssueDetailClient {...defaultProps} />)

    // Submit PR
    const submitPRButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitPRButton)

    await waitFor(() => {
      expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    })

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/999' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    // Wait for celebration
    await waitFor(() => {
      expect(screen.getByText(/pr submitted!/i)).toBeInTheDocument()
    })

    // Close celebration
    const continueButton = screen.getByRole('button', { name: /continue/i })
    fireEvent.click(continueButton)

    // PR management should load
    await waitFor(() => {
      expect(contributionsApi.getUserContributions).toHaveBeenCalledWith(789, 'test-token')
    })
  })

  it('does not show submit button for issues not claimed by current user', () => {
    const unclaimedIssue = {
      ...mockIssue,
      status: 'available' as const,
      claimed_by: null,
      claimed_at: null,
      claim_expires_at: null,
    }

    render(<IssueDetailClient {...defaultProps} issue={unclaimedIssue} />)

    // Submit PR button should not be visible
    expect(screen.queryByRole('button', { name: /submit pull request/i })).not.toBeInTheDocument()
  })

  it('does not show submit button for issues claimed by other users', () => {
    const otherUserIssue = {
      ...mockIssue,
      claimed_by: 999, // Different user
    }

    render(<IssueDetailClient {...defaultProps} issue={otherUserIssue} />)

    // Submit PR button should not be visible
    expect(screen.queryByRole('button', { name: /submit pull request/i })).not.toBeInTheDocument()
  })
})
