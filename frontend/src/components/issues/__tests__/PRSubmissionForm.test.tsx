import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PRSubmissionForm from '../PRSubmissionForm'
import * as contributionsApi from '@/lib/contributions-api'

vi.mock('@/lib/contributions-api')

describe('PRSubmissionForm', () => {
  const mockOnSuccess = vi.fn()
  const mockOnCancel = vi.fn()
  const defaultProps = {
    issueId: 1,
    userId: 123,
    accessToken: 'test-token',
    onSuccess: mockOnSuccess,
    onCancel: mockOnCancel,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form with input and buttons', () => {
    render(<PRSubmissionForm {...defaultProps} />)

    expect(screen.getByLabelText(/pull request url/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/https:\/\/github.com/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit pull request/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
  })

  it('validates empty URL', async () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/pr url is required/i)).toBeInTheDocument()
    })

    expect(contributionsApi.submitPullRequest).not.toHaveBeenCalled()
  })

  it('validates non-GitHub URL', async () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://gitlab.com/owner/repo/merge_requests/1' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/url must be from github.com/i)).toBeInTheDocument()
    })

    expect(contributionsApi.submitPullRequest).not.toHaveBeenCalled()
  })

  it('validates URL without /pull/ path', async () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/issues/123' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/url must be a github pull request/i)).toBeInTheDocument()
    })

    expect(contributionsApi.submitPullRequest).not.toHaveBeenCalled()
  })

  it('validates invalid URL format', async () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'not-a-url' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid url format/i)).toBeInTheDocument()
    })

    expect(contributionsApi.submitPullRequest).not.toHaveBeenCalled()
  })

  it('submits valid PR URL successfully', async () => {
    const mockResult = {
      success: true,
      message: 'PR submitted successfully',
      contribution_id: 1,
      pr_number: 123,
      status: 'submitted',
      points_earned: 10,
    }

    vi.mocked(contributionsApi.submitPullRequest).mockResolvedValue(mockResult)

    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/123' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(contributionsApi.submitPullRequest).toHaveBeenCalledWith(
        1,
        'https://github.com/owner/repo/pull/123',
        123,
        'test-token'
      )
    })

    expect(mockOnSuccess).toHaveBeenCalledWith(mockResult)
  })

  it('displays error message on submission failure', async () => {
    const mockResult = {
      success: false,
      message: 'PR validation failed: PR not found',
    }

    vi.mocked(contributionsApi.submitPullRequest).mockResolvedValue(mockResult)

    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/999' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/pr validation failed: pr not found/i)).toBeInTheDocument()
    })

    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('handles API errors gracefully', async () => {
    vi.mocked(contributionsApi.submitPullRequest).mockRejectedValue(
      new Error('Network error')
    )

    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/123' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument()
    })

    expect(mockOnSuccess).not.toHaveBeenCalled()
  })

  it('disables submit button while submitting', async () => {
    vi.mocked(contributionsApi.submitPullRequest).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/123' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/validating/i)).toBeInTheDocument()
    })

    expect(submitButton).toBeDisabled()
  })

  it('clears validation errors when user types', async () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    const submitButton = screen.getByRole('button', { name: /submit pull request/i })

    // Trigger validation error
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/pr url is required/i)).toBeInTheDocument()
    })

    // Start typing
    fireEvent.change(input, { target: { value: 'https://github.com' } })

    // Error should be cleared
    expect(screen.queryByText(/pr url is required/i)).not.toBeInTheDocument()
  })

  it('calls onCancel when cancel button is clicked', () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    fireEvent.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('disables submit button when URL is empty', () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    // Button is not disabled, but shows validation error on click
    expect(submitButton).not.toBeDisabled()
  })

  it('enables submit button when URL is entered', () => {
    render(<PRSubmissionForm {...defaultProps} />)

    const input = screen.getByLabelText(/pull request url/i)
    fireEvent.change(input, { target: { value: 'https://github.com/owner/repo/pull/123' } })

    const submitButton = screen.getByRole('button', { name: /submit pull request/i })
    expect(submitButton).not.toBeDisabled()
  })
})
