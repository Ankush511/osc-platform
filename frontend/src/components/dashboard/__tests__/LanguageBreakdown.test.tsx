import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import LanguageBreakdown from '../LanguageBreakdown'

describe('LanguageBreakdown', () => {
  it('renders empty state when no contributions', () => {
    render(<LanguageBreakdown contributions={{}} />)
    
    expect(screen.getByText(/No language data available yet/i)).toBeInTheDocument()
  })

  it('renders language contributions correctly', () => {
    const contributions = {
      Python: 10,
      JavaScript: 5,
      TypeScript: 3,
    }
    
    render(<LanguageBreakdown contributions={contributions} />)
    
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
  })

  it('displays correct counts and percentages', () => {
    const contributions = {
      Python: 10,
      JavaScript: 5,
      TypeScript: 5,
    }
    
    render(<LanguageBreakdown contributions={contributions} />)
    
    expect(screen.getByText('10 (50.0%)')).toBeInTheDocument()
    const percentages = screen.getAllByText('5 (25.0%)')
    expect(percentages).toHaveLength(2)
  })

  it('sorts languages by contribution count descending', () => {
    const contributions = {
      JavaScript: 5,
      Python: 10,
      TypeScript: 3,
    }
    
    const { container } = render(<LanguageBreakdown contributions={contributions} />)
    const languages = container.querySelectorAll('.text-sm.font-medium.text-gray-700')
    
    expect(languages[0].textContent).toBe('Python')
    expect(languages[1].textContent).toBe('JavaScript')
    expect(languages[2].textContent).toBe('TypeScript')
  })

  it('renders progress bars with correct widths', () => {
    const contributions = {
      Python: 10,
      JavaScript: 5,
    }
    
    const { container } = render(<LanguageBreakdown contributions={contributions} />)
    const progressBars = container.querySelectorAll('.h-2\\.5.rounded-full:not(.bg-gray-200)')
    
    // Check that progress bars exist and have inline styles
    expect(progressBars[0]).toHaveAttribute('style', expect.stringContaining('width'))
    expect(progressBars[1]).toHaveAttribute('style', expect.stringContaining('width'))
  })

  it('handles single language correctly', () => {
    const contributions = {
      Python: 5,
    }
    
    render(<LanguageBreakdown contributions={contributions} />)
    
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('5 (100.0%)')).toBeInTheDocument()
  })
})
