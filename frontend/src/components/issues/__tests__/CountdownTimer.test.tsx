import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import CountdownTimer from '../CountdownTimer'

describe('CountdownTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('displays days and hours when more than 1 day remaining', () => {
    const futureDate = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000) // 2 days from now
    render(<CountdownTimer expiresAt={futureDate.toISOString()} />)
    
    expect(screen.getByText(/\d+d \d+h/)).toBeInTheDocument()
  })

  it('displays hours and minutes when less than 1 day remaining', () => {
    const futureDate = new Date(Date.now() + 5 * 60 * 60 * 1000) // 5 hours from now
    render(<CountdownTimer expiresAt={futureDate.toISOString()} />)
    
    expect(screen.getByText(/\d+h \d+m/)).toBeInTheDocument()
  })

  it('displays minutes when less than 1 hour remaining', () => {
    const futureDate = new Date(Date.now() + 30 * 60 * 1000) // 30 minutes from now
    render(<CountdownTimer expiresAt={futureDate.toISOString()} />)
    
    expect(screen.getByText(/\d+m/)).toBeInTheDocument()
  })

  it('displays "Expired" when time has passed', () => {
    const pastDate = new Date(Date.now() - 1000) // 1 second ago
    render(<CountdownTimer expiresAt={pastDate.toISOString()} />)
    
    expect(screen.getByText('Expired')).toBeInTheDocument()
  })

  it('applies red text color when expired', () => {
    const pastDate = new Date(Date.now() - 1000)
    const { container } = render(<CountdownTimer expiresAt={pastDate.toISOString()} />)
    
    const timer = screen.getByText('Expired')
    expect(timer.className).toContain('text-red-600')
  })

  it('applies custom className', () => {
    const futureDate = new Date(Date.now() + 1000)
    const { container } = render(<CountdownTimer expiresAt={futureDate.toISOString()} className="custom-class" />)
    
    const timer = container.querySelector('.custom-class')
    expect(timer).toBeInTheDocument()
  })
})
