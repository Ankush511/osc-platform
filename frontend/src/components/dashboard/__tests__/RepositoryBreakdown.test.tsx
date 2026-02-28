import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import RepositoryBreakdown from '../RepositoryBreakdown'

describe('RepositoryBreakdown', () => {
  it('renders empty state when no contributions', () => {
    render(<RepositoryBreakdown contributions={{}} />)
    
    expect(screen.getByText(/No repository data available yet/i)).toBeInTheDocument()
  })

  it('renders repository contributions correctly', () => {
    const contributions = {
      'facebook/react': 5,
      'microsoft/vscode': 3,
      'nodejs/node': 2,
    }
    
    render(<RepositoryBreakdown contributions={contributions} />)
    
    expect(screen.getByText('facebook/react')).toBeInTheDocument()
    expect(screen.getByText('microsoft/vscode')).toBeInTheDocument()
    expect(screen.getByText('nodejs/node')).toBeInTheDocument()
  })

  it('displays correct contribution counts', () => {
    const contributions = {
      'facebook/react': 5,
      'microsoft/vscode': 1,
    }
    
    render(<RepositoryBreakdown contributions={contributions} />)
    
    expect(screen.getByText('5 contributions')).toBeInTheDocument()
    expect(screen.getByText('1 contribution')).toBeInTheDocument()
  })

  it('sorts repositories by contribution count descending', () => {
    const contributions = {
      'microsoft/vscode': 3,
      'facebook/react': 5,
      'nodejs/node': 2,
    }
    
    const { container } = render(<RepositoryBreakdown contributions={contributions} />)
    const repos = container.querySelectorAll('.text-sm.font-medium.text-gray-900')
    
    expect(repos[0].textContent).toBe('facebook/react')
    expect(repos[1].textContent).toBe('microsoft/vscode')
    expect(repos[2].textContent).toBe('nodejs/node')
  })

  it('limits display to top 10 repositories', () => {
    const contributions: Record<string, number> = {}
    for (let i = 1; i <= 15; i++) {
      contributions[`owner/repo${i}`] = 15 - i
    }
    
    const { container } = render(<RepositoryBreakdown contributions={contributions} />)
    const repos = container.querySelectorAll('.text-sm.font-medium.text-gray-900')
    
    expect(repos).toHaveLength(10)
  })

  it('renders GitHub links correctly', () => {
    const contributions = {
      'facebook/react': 5,
    }
    
    render(<RepositoryBreakdown contributions={contributions} />)
    
    const link = screen.getByText('facebook/react')
    expect(link).toHaveAttribute('href', 'https://github.com/facebook/react')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('handles single repository correctly', () => {
    const contributions = {
      'facebook/react': 1,
    }
    
    render(<RepositoryBreakdown contributions={contributions} />)
    
    expect(screen.getByText('facebook/react')).toBeInTheDocument()
    expect(screen.getByText('1 contribution')).toBeInTheDocument()
  })
})
