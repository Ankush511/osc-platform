import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import PRStatusDisplay from '../PRStatusDisplay'
import { Contribution } from '@/types/contribution'

describe('PRStatusDisplay', () => {
  const baseContribution: Contribution = {
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

  it('renders submitted PR status correctly', () => {
    render(<PRStatusDisplay contribution={baseContribution} />)

    expect(screen.getByText(/pending review/i)).toBeInTheDocument()
    expect(screen.getByText(/your pull request is under review/i)).toBeInTheDocument()
    expect(screen.getByText(/\+10 points/i)).toBeInTheDocument()
    expect(screen.getByText(/PR #789/i)).toBeInTheDocument()
  })

  it('renders merged PR status correctly', () => {
    const mergedContribution: Contribution = {
      ...baseContribution,
      status: 'merged',
      merged_at: '2024-01-16T14:30:00Z',
      points_earned: 100,
    }

    render(<PRStatusDisplay contribution={mergedContribution} />)

    expect(screen.getByRole('heading', { name: /merged/i })).toBeInTheDocument()
    expect(screen.getByText(/your pull request has been merged/i)).toBeInTheDocument()
    expect(screen.getByText(/\+100 points/i)).toBeInTheDocument()
    expect(screen.getByText(/PR #789/i)).toBeInTheDocument()
  })

  it('renders closed PR status correctly', () => {
    const closedContribution: Contribution = {
      ...baseContribution,
      status: 'closed',
      points_earned: 0,
    }

    render(<PRStatusDisplay contribution={closedContribution} />)

    expect(screen.getByRole('heading', { name: /closed/i })).toBeInTheDocument()
    expect(screen.getByText(/this pull request was closed without merging/i)).toBeInTheDocument()
    expect(screen.getByText(/\+0 points/i)).toBeInTheDocument()
  })

  it('displays GitHub link', () => {
    render(<PRStatusDisplay contribution={baseContribution} />)

    const link = screen.getByRole('link', { name: /view on github/i })
    expect(link).toHaveAttribute('href', 'https://github.com/owner/repo/pull/789')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('displays submitted date', () => {
    render(<PRStatusDisplay contribution={baseContribution} />)

    expect(screen.getByText(/submitted:/i)).toBeInTheDocument()
  })

  it('displays merged date when PR is merged', () => {
    const mergedContribution: Contribution = {
      ...baseContribution,
      status: 'merged',
      merged_at: '2024-01-16T14:30:00Z',
      points_earned: 100,
    }

    render(<PRStatusDisplay contribution={mergedContribution} />)

    expect(screen.getByText(/merged:/i)).toBeInTheDocument()
  })

  it('does not display merged date when PR is not merged', () => {
    render(<PRStatusDisplay contribution={baseContribution} />)

    expect(screen.queryByText(/merged:/i)).not.toBeInTheDocument()
  })

  it('applies correct styling for submitted status', () => {
    const { container } = render(<PRStatusDisplay contribution={baseContribution} />)

    const statusContainer = container.querySelector('.bg-blue-100')
    expect(statusContainer).toBeInTheDocument()
  })

  it('applies correct styling for merged status', () => {
    const mergedContribution: Contribution = {
      ...baseContribution,
      status: 'merged',
      merged_at: '2024-01-16T14:30:00Z',
      points_earned: 100,
    }

    const { container } = render(<PRStatusDisplay contribution={mergedContribution} />)

    const statusContainer = container.querySelector('.bg-green-100')
    expect(statusContainer).toBeInTheDocument()
  })

  it('applies correct styling for closed status', () => {
    const closedContribution: Contribution = {
      ...baseContribution,
      status: 'closed',
      points_earned: 0,
    }

    const { container } = render(<PRStatusDisplay contribution={closedContribution} />)

    const statusContainer = container.querySelector('.bg-gray-100')
    expect(statusContainer).toBeInTheDocument()
  })
})
