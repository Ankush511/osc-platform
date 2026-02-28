import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import IssueCard from '../IssueCard'
import { Issue } from '@/types/issue'

describe('IssueCard', () => {
  const mockIssue: Issue = {
    id: 1,
    github_issue_id: 123,
    repository_id: 1,
    title: 'Fix bug in authentication',
    description: 'The login form is not validating email addresses correctly',
    labels: ['bug', 'good first issue', 'help wanted'],
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

  it('renders issue title', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('Fix bug in authentication')).toBeInTheDocument()
  })

  it('renders repository name', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('test/test-repo')).toBeInTheDocument()
  })

  it('renders issue description', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText(/The login form is not validating/)).toBeInTheDocument()
  })

  it('renders programming language badge', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
  })

  it('renders difficulty level badge', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('easy')).toBeInTheDocument()
  })

  it('renders status badge', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('available')).toBeInTheDocument()
  })

  it('renders first 3 labels', () => {
    render(<IssueCard issue={mockIssue} />)
    expect(screen.getByText('bug')).toBeInTheDocument()
    expect(screen.getByText('good first issue')).toBeInTheDocument()
    expect(screen.getByText('help wanted')).toBeInTheDocument()
  })

  it('shows +X more when there are more than 3 labels', () => {
    const issueWithManyLabels: Issue = {
      ...mockIssue,
      labels: ['bug', 'good first issue', 'help wanted', 'enhancement', 'documentation'],
    }

    render(<IssueCard issue={issueWithManyLabels} />)
    expect(screen.getByText('+2 more')).toBeInTheDocument()
  })

  it('renders claimed info when issue is claimed', () => {
    const claimedIssue: Issue = {
      ...mockIssue,
      status: 'claimed',
      claimed_by: 1,
      claimed_at: '2024-01-01T00:00:00Z',
      claim_expires_at: '2024-01-08T00:00:00Z',
    }

    render(<IssueCard issue={claimedIssue} />)
    expect(screen.getByText(/Claimed • Expires/)).toBeInTheDocument()
  })

  it('does not render description when null', () => {
    const issueWithoutDescription: Issue = {
      ...mockIssue,
      description: null,
    }

    render(<IssueCard issue={issueWithoutDescription} />)
    expect(screen.queryByText(/The login form/)).not.toBeInTheDocument()
  })

  it('applies correct difficulty color classes', () => {
    const { container } = render(<IssueCard issue={mockIssue} />)
    const difficultyBadge = screen.getByText('easy')
    expect(difficultyBadge.className).toContain('bg-green-100')
  })

  it('wraps card in link to issue detail page', () => {
    render(<IssueCard issue={mockIssue} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/issues/1')
  })
})
