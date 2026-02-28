import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ContributionTimeline from '../ContributionTimeline'
import { RecentContribution } from '@/types/dashboard'

describe('ContributionTimeline', () => {
  const mockContributions: RecentContribution[] = [
    {
      contribution_id: 1,
      issue_title: 'Fix login bug',
      repository: 'owner/repo1',
      status: 'merged',
      pr_url: 'https://github.com/owner/repo1/pull/1',
      submitted_at: '2024-01-15T00:00:00Z',
      merged_at: '2024-01-16T00:00:00Z',
    },
    {
      contribution_id: 2,
      issue_title: 'Add documentation',
      repository: 'owner/repo2',
      status: 'submitted',
      pr_url: 'https://github.com/owner/repo2/pull/2',
      submitted_at: '2024-01-14T00:00:00Z',
      merged_at: null,
    },
    {
      contribution_id: 3,
      issue_title: 'Update dependencies',
      repository: 'owner/repo3',
      status: 'closed',
      pr_url: 'https://github.com/owner/repo3/pull/3',
      submitted_at: '2024-01-13T00:00:00Z',
      merged_at: null,
    },
  ]

  it('renders empty state when no contributions', () => {
    render(<ContributionTimeline contributions={[]} />)
    
    expect(screen.getByText(/No contributions yet/i)).toBeInTheDocument()
  })

  it('renders all contributions by default', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    expect(screen.getByText('Fix login bug')).toBeInTheDocument()
    expect(screen.getByText('Add documentation')).toBeInTheDocument()
    expect(screen.getByText('Update dependencies')).toBeInTheDocument()
  })

  it('renders filter buttons', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    expect(screen.getByText('All')).toBeInTheDocument()
    expect(screen.getByText('Merged')).toBeInTheDocument()
    expect(screen.getByText('Pending')).toBeInTheDocument()
    expect(screen.getByText('Closed')).toBeInTheDocument()
  })

  it('filters contributions by merged status', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    const mergedButton = screen.getByText('Merged')
    fireEvent.click(mergedButton)
    
    expect(screen.getByText('Fix login bug')).toBeInTheDocument()
    expect(screen.queryByText('Add documentation')).not.toBeInTheDocument()
    expect(screen.queryByText('Update dependencies')).not.toBeInTheDocument()
  })

  it('filters contributions by submitted status', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    const pendingButton = screen.getByText('Pending')
    fireEvent.click(pendingButton)
    
    expect(screen.queryByText('Fix login bug')).not.toBeInTheDocument()
    expect(screen.getByText('Add documentation')).toBeInTheDocument()
    expect(screen.queryByText('Update dependencies')).not.toBeInTheDocument()
  })

  it('filters contributions by closed status', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    const closedButton = screen.getByText('Closed')
    fireEvent.click(closedButton)
    
    expect(screen.queryByText('Fix login bug')).not.toBeInTheDocument()
    expect(screen.queryByText('Add documentation')).not.toBeInTheDocument()
    expect(screen.getByText('Update dependencies')).toBeInTheDocument()
  })

  it('shows empty state when filter has no results', () => {
    const mergedOnly: RecentContribution[] = [mockContributions[0]]
    render(<ContributionTimeline contributions={mergedOnly} />)
    
    const pendingButton = screen.getByText('Pending')
    fireEvent.click(pendingButton)
    
    expect(screen.getByText(/No submitted contributions found/i)).toBeInTheDocument()
  })

  it('renders PR links correctly', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    const links = screen.getAllByText('View PR →')
    expect(links).toHaveLength(3)
    expect(links[0]).toHaveAttribute('href', 'https://github.com/owner/repo1/pull/1')
  })

  it('displays correct status badges', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    expect(screen.getByText('merged')).toBeInTheDocument()
    expect(screen.getByText('submitted')).toBeInTheDocument()
    expect(screen.getByText('closed')).toBeInTheDocument()
  })

  it('formats dates correctly', () => {
    render(<ContributionTimeline contributions={mockContributions} />)
    
    expect(screen.getByText('Jan 15, 2024')).toBeInTheDocument()
    expect(screen.getByText('Jan 14, 2024')).toBeInTheDocument()
    expect(screen.getByText('Jan 13, 2024')).toBeInTheDocument()
  })
})
