import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatsCard from '../StatsCard'

describe('StatsCard', () => {
  it('renders with title and value', () => {
    render(<StatsCard title="Total Contributions" value={42} />)
    
    expect(screen.getByText('Total Contributions')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders with icon when provided', () => {
    render(<StatsCard title="PRs Merged" value={10} icon="✅" />)
    
    expect(screen.getByText('✅')).toBeInTheDocument()
  })

  it('renders with description when provided', () => {
    render(
      <StatsCard
        title="Achievements"
        value="5/10"
        description="50% complete"
      />
    )
    
    expect(screen.getByText('50% complete')).toBeInTheDocument()
  })

  it('handles string values', () => {
    render(<StatsCard title="Status" value="Active" />)
    
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('handles numeric values', () => {
    render(<StatsCard title="Count" value={0} />)
    
    expect(screen.getByText('0')).toBeInTheDocument()
  })
})
