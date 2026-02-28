import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ContributionCelebration from '../ContributionCelebration'
import { SubmissionResult } from '@/types/contribution'

describe('ContributionCelebration', () => {
  const mockOnClose = vi.fn()

  const submittedResult: SubmissionResult = {
    success: true,
    message: 'PR submitted successfully',
    contribution_id: 1,
    pr_number: 123,
    status: 'submitted',
    points_earned: 10,
  }

  const mergedResult: SubmissionResult = {
    success: true,
    message: 'PR merged successfully',
    contribution_id: 1,
    pr_number: 123,
    status: 'merged',
    points_earned: 100,
  }

  it('renders celebration for submitted PR', () => {
    render(<ContributionCelebration result={submittedResult} onClose={mockOnClose} />)

    expect(screen.getByText(/pr submitted!/i)).toBeInTheDocument()
    expect(screen.getByText(/your pull request has been submitted successfully/i)).toBeInTheDocument()
    expect(screen.getByText(/#123/i)).toBeInTheDocument()
    expect(screen.getByText(/\+10/i)).toBeInTheDocument()
  })

  it('renders celebration for merged PR', () => {
    render(<ContributionCelebration result={mergedResult} onClose={mockOnClose} />)

    expect(screen.getByText(/contribution merged!/i)).toBeInTheDocument()
    expect(screen.getByText(/your pull request has been merged/i)).toBeInTheDocument()
    expect(screen.getByText(/#123/i)).toBeInTheDocument()
    expect(screen.getByText(/\+100/i)).toBeInTheDocument()
  })

  it('displays different encouragement for submitted vs merged', () => {
    const { rerender } = render(
      <ContributionCelebration result={submittedResult} onClose={mockOnClose} />
    )

    expect(screen.getByText(/hang tight! maintainers will review your pr soon/i)).toBeInTheDocument()

    rerender(<ContributionCelebration result={mergedResult} onClose={mockOnClose} />)

    expect(screen.getByText(/keep up the great work/i)).toBeInTheDocument()
  })

  it('displays PR number and points earned', () => {
    render(<ContributionCelebration result={submittedResult} onClose={mockOnClose} />)

    expect(screen.getByText(/#123/i)).toBeInTheDocument()
    expect(screen.getByText(/\+10/i)).toBeInTheDocument()
  })

  it('has a link to view on GitHub', () => {
    render(<ContributionCelebration result={submittedResult} onClose={mockOnClose} />)

    const githubLink = screen.getByRole('link', { name: /view on github/i })
    expect(githubLink).toHaveAttribute('href', 'https://github.com/pulls')
    expect(githubLink).toHaveAttribute('target', '_blank')
  })

  it('calls onClose when continue button is clicked', () => {
    render(<ContributionCelebration result={submittedResult} onClose={mockOnClose} />)

    const continueButton = screen.getByRole('button', { name: /continue/i })
    fireEvent.click(continueButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('displays success icon', () => {
    const { container } = render(
      <ContributionCelebration result={submittedResult} onClose={mockOnClose} />
    )

    // Check for the checkmark SVG
    const checkmark = container.querySelector('svg path[d*="M5 13l4 4L19 7"]')
    expect(checkmark).toBeInTheDocument()
  })
})
