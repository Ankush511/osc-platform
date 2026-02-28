import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorMessage } from '../ErrorMessage'

describe('ErrorMessage', () => {
  it('should render error message', () => {
    render(<ErrorMessage message="Test error message" />)

    expect(screen.getByText('Error')).toBeInTheDocument()
    expect(screen.getByText('Test error message')).toBeInTheDocument()
  })

  it('should render custom title', () => {
    render(<ErrorMessage title="Custom Error" message="Test message" />)

    expect(screen.getByText('Custom Error')).toBeInTheDocument()
  })

  it('should render retry button when onRetry is provided', () => {
    const onRetry = vi.fn()
    render(<ErrorMessage message="Test error" onRetry={onRetry} />)

    const retryButton = screen.getByText('Try again')
    expect(retryButton).toBeInTheDocument()

    fireEvent.click(retryButton)
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('should not render retry button when onRetry is not provided', () => {
    render(<ErrorMessage message="Test error" />)

    expect(screen.queryByText('Try again')).not.toBeInTheDocument()
  })

  it('should apply error variant styles', () => {
    const { container } = render(
      <ErrorMessage message="Test error" variant="error" />
    )

    const errorContainer = container.querySelector('.bg-red-50')
    expect(errorContainer).toBeInTheDocument()
  })

  it('should apply warning variant styles', () => {
    const { container } = render(
      <ErrorMessage message="Test warning" variant="warning" />
    )

    const warningContainer = container.querySelector('.bg-yellow-50')
    expect(warningContainer).toBeInTheDocument()
  })

  it('should apply info variant styles', () => {
    const { container } = render(
      <ErrorMessage message="Test info" variant="info" />
    )

    const infoContainer = container.querySelector('.bg-blue-50')
    expect(infoContainer).toBeInTheDocument()
  })
})
