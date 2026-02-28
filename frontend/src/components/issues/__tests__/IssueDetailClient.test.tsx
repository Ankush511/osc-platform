import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import IssueDetailClient from '../IssueDetailClient'
import { Issue } from '@/types/issue'
import { IssueExplanationResponse, RepositorySummaryResponse } from '@/types/ai'
import * as issuesApi from '@/lib/issues-api'
import { useRouter } from 'next/navigation'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}))

// Mock issues API
vi.mock('@/lib/issues-api', () => ({
  claimIssue: vi.fn(),
  releaseIssue: vi.fn(),
  extendClaimDeadline: vi.fn(),
}))

describe('IssueDetailClient', () => {
  const mockRouter = {
    push: vi.fn(),
  }

  const mockIssue: Issue = {
    id: 1,
    github_issue_id: 123,
    repository_id: 1,
    title: 'Fix bug in authentication',
    description: 'The login form is not validating email addresses correctly',
    labels: ['bug', 'good first issue'],
    programming_language: 'JavaScript',
    difficulty_level: 'easy',
    ai_explanation: null,
    status: 'available',
    claimed_by: null,
    claimed_at: null,
    claim_expires_at: null,
    github_url: 'https://github.com/test/repo/issues/123',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    repository_name: 'test-repo',
    repository_full_name: 'test/test-repo',
  }

  const mockRepoSummary: RepositorySummaryResponse = {
    repository_id: 1,
    summary: 'This is a test repository for learning purposes.',
    cached: false,
  }

  const mockIssueExplanation: IssueExplanationResponse = {
    issue_id: 1,
    explanation: 'This issue requires fixing the email validation logic.',
    difficulty_level: 'easy',
    learning_resources: [
      {
        title: 'Email Validation Guide',
        url: 'https://example.com/guide',
        type: 'tutorial',
        description: 'Learn about email validation',
      },
    ],
    cached: false,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as any).mockReturnValue(mockRouter)
    window.open = vi.fn()
    window.confirm = vi.fn(() => true)
  })

  it('renders issue title and repository name', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('Fix bug in authentication')).toBeInTheDocument()
    expect(screen.getByText('test/test-repo')).toBeInTheDocument()
  })

  it('renders repository summary', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('This is a test repository for learning purposes.')).toBeInTheDocument()
  })

  it('renders AI explanation', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('This issue requires fixing the email validation logic.')).toBeInTheDocument()
  })

  it('renders learning resources', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('Email Validation Guide')).toBeInTheDocument()
  })

  it('shows "Solve It" button for available issues', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('Solve It')).toBeInTheDocument()
  })

  it('claims issue and redirects to GitHub when "Solve It" is clicked', async () => {
    const mockClaimResult = {
      success: true,
      message: 'Issue claimed successfully',
      issue_id: 1,
      claimed_at: '2024-01-01T00:00:00Z',
      claim_expires_at: '2024-01-08T00:00:00Z',
    }

    vi.mocked(issuesApi.claimIssue).mockResolvedValue(mockClaimResult)

    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    const solveButton = screen.getByText('Solve It')
    fireEvent.click(solveButton)

    await waitFor(() => {
      expect(issuesApi.claimIssue).toHaveBeenCalledWith(1, 1, 'test-token')
      expect(window.open).toHaveBeenCalledWith('https://github.com/test/repo/issues/123', '_blank')
    })
  })

  it('shows action buttons for claimed issue by current user', () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 1,
      claimed_at: '2024-01-01T00:00:00Z',
      claim_expires_at: '2024-01-08T00:00:00Z',
    }

    render(
      <IssueDetailClient
        issue={claimedIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('Go to GitHub')).toBeInTheDocument()
    expect(screen.getByText('Release Issue')).toBeInTheDocument()
    expect(screen.getByText('Extend Deadline')).toBeInTheDocument()
  })

  it('releases issue when "Release Issue" is clicked', async () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 1,
    }

    const mockReleaseResult = {
      success: true,
      message: 'Issue released successfully',
      issue_id: 1,
    }

    vi.mocked(issuesApi.releaseIssue).mockResolvedValue(mockReleaseResult)

    render(
      <IssueDetailClient
        issue={claimedIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    const releaseButton = screen.getByText('Release Issue')
    fireEvent.click(releaseButton)

    await waitFor(() => {
      expect(issuesApi.releaseIssue).toHaveBeenCalledWith(1, 1, 'test-token')
    })
  })

  it('opens extend deadline modal when "Extend Deadline" is clicked', () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 1,
    }

    render(
      <IssueDetailClient
        issue={claimedIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    const extendButton = screen.getByText('Extend Deadline')
    fireEvent.click(extendButton)

    expect(screen.getByText('Justification (min 10 characters)')).toBeInTheDocument()
  })

  it('extends deadline with valid justification', async () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 1,
    }

    const mockExtensionResult = {
      success: true,
      message: 'Deadline extended',
      issue_id: 1,
      new_expiration: '2024-01-15T00:00:00Z',
    }

    vi.mocked(issuesApi.extendClaimDeadline).mockResolvedValue(mockExtensionResult)

    render(
      <IssueDetailClient
        issue={claimedIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    // Open modal
    const extendButton = screen.getByText('Extend Deadline')
    fireEvent.click(extendButton)

    // Fill in justification
    const textarea = screen.getByPlaceholderText('Explain why you need more time...')
    fireEvent.change(textarea, { target: { value: 'I need more time to complete the work' } })

    // Submit
    const submitButton = screen.getByRole('button', { name: 'Extend' })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(issuesApi.extendClaimDeadline).toHaveBeenCalledWith(
        1,
        1,
        7,
        'I need more time to complete the work',
        'test-token'
      )
    })
  })

  it('shows "View on GitHub" button for issues claimed by others', () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 2, // Different user
    }

    render(
      <IssueDetailClient
        issue={claimedIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    expect(screen.getByText('View on GitHub')).toBeInTheDocument()
    expect(screen.queryByText('Release Issue')).not.toBeInTheDocument()
  })

  it('displays error message when claim fails', async () => {
    vi.mocked(issuesApi.claimIssue).mockRejectedValue(new Error('Issue already claimed'))

    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    const solveButton = screen.getByText('Solve It')
    fireEvent.click(solveButton)

    await waitFor(() => {
      expect(screen.getByText('Issue already claimed')).toBeInTheDocument()
    })
  })

  it('navigates back to issues list when "Back to Issues" is clicked', () => {
    render(
      <IssueDetailClient
        issue={mockIssue}
        repositorySummary={mockRepoSummary}
        issueExplanation={mockIssueExplanation}
        accessToken="test-token"
        currentUserId={1}
      />
    )

    const backButton = screen.getByText('Back to Issues')
    fireEvent.click(backButton)

    expect(mockRouter.push).toHaveBeenCalledWith('/issues')
  })
})
