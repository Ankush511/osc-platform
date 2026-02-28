import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import IssueList from '../IssueList'
import { PaginatedIssuesResponse, Issue } from '@/types/issue'

describe('IssueList', () => {
  const mockIssue: Issue = {
    id: 1,
    github_issue_id: 123,
    repository_id: 1,
    title: 'Test Issue',
    description: 'Test description',
    labels: ['bug'],
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

  const mockIssuesData: PaginatedIssuesResponse = {
    items: [mockIssue],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
  }

  it('shows loading state', () => {
    const onPageChange = vi.fn()
    render(
      <IssueList
        issuesData={null}
        loading={true}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    const loadingElements = screen.getAllByRole('generic')
    const animatedElements = loadingElements.filter(el => 
      el.className.includes('animate-pulse')
    )
    expect(animatedElements.length).toBeGreaterThan(0)
  })

  it('shows error state', () => {
    const onPageChange = vi.fn()
    render(
      <IssueList
        issuesData={null}
        loading={false}
        error="Failed to load issues"
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    expect(screen.getByText('Error Loading Issues')).toBeInTheDocument()
    expect(screen.getByText('Failed to load issues')).toBeInTheDocument()
  })

  it('shows empty state when no issues', () => {
    const onPageChange = vi.fn()
    const emptyData: PaginatedIssuesResponse = {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    }

    render(
      <IssueList
        issuesData={emptyData}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    expect(screen.getByText('No Issues Found')).toBeInTheDocument()
    expect(screen.getByText(/Try adjusting your filters/)).toBeInTheDocument()
  })

  it('renders issue cards when data is available', () => {
    const onPageChange = vi.fn()
    render(
      <IssueList
        issuesData={mockIssuesData}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    expect(screen.getByText('Test Issue')).toBeInTheDocument()
  })

  it('shows results count', () => {
    const onPageChange = vi.fn()
    const dataWithMultipleIssues: PaginatedIssuesResponse = {
      items: [mockIssue, { ...mockIssue, id: 2, title: 'Second Issue' }],
      total: 50,
      page: 1,
      page_size: 20,
      total_pages: 3,
    }

    render(
      <IssueList
        issuesData={dataWithMultipleIssues}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    expect(screen.getByText('Showing 2 of 50 issues')).toBeInTheDocument()
  })

  it('renders pagination when there are multiple pages', () => {
    const onPageChange = vi.fn()
    const dataWithMultiplePages: PaginatedIssuesResponse = {
      items: [mockIssue],
      total: 50,
      page: 1,
      page_size: 20,
      total_pages: 3,
    }

    render(
      <IssueList
        issuesData={dataWithMultiplePages}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    // Check for pagination buttons
    const page1Button = screen.getByRole('button', { name: '1' })
    expect(page1Button).toBeInTheDocument()
    expect(page1Button.className).toContain('bg-blue-600')
  })

  it('does not render pagination when there is only one page', () => {
    const onPageChange = vi.fn()
    render(
      <IssueList
        issuesData={mockIssuesData}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    expect(screen.queryByText(/Page/)).not.toBeInTheDocument()
  })

  it('calls onPageChange when pagination is used', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    
    const dataWithMultiplePages: PaginatedIssuesResponse = {
      items: [mockIssue],
      total: 50,
      page: 1,
      page_size: 20,
      total_pages: 3,
    }

    render(
      <IssueList
        issuesData={dataWithMultiplePages}
        loading={false}
        error={null}
        currentPage={1}
        onPageChange={onPageChange}
      />
    )

    const nextButton = screen.getAllByRole('button', { name: /next/i })[1]
    await user.click(nextButton)

    expect(onPageChange).toHaveBeenCalledWith(2)
  })
})
