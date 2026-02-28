import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FilterSidebar from '../FilterSidebar'
import { AvailableFilters, IssueFilters } from '@/types/issue'

describe('FilterSidebar', () => {
  const mockAvailableFilters: AvailableFilters = {
    programming_languages: ['JavaScript', 'Python', 'TypeScript'],
    labels: ['good first issue', 'bug', 'enhancement'],
    difficulty_levels: ['easy', 'medium', 'hard'],
  }

  it('renders all filter sections', () => {
    const onFilterChange = vi.fn()
    render(
      <FilterSidebar
        filters={{}}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    expect(screen.getByText('Programming Language')).toBeInTheDocument()
    expect(screen.getByText('Labels')).toBeInTheDocument()
    expect(screen.getByText('Difficulty')).toBeInTheDocument()
  })

  it('displays available programming languages', () => {
    const onFilterChange = vi.fn()
    render(
      <FilterSidebar
        filters={{}}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    expect(screen.getByText('JavaScript')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
  })

  it('toggles language filter when checkbox is clicked', async () => {
    const onFilterChange = vi.fn()
    const user = userEvent.setup()
    
    render(
      <FilterSidebar
        filters={{}}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    const checkbox = screen.getByRole('checkbox', { name: /javascript/i })
    await user.click(checkbox)

    expect(onFilterChange).toHaveBeenCalledWith({
      programming_languages: ['JavaScript'],
    })
  })

  it('removes language filter when unchecking', async () => {
    const onFilterChange = vi.fn()
    const user = userEvent.setup()
    
    const filters: IssueFilters = {
      programming_languages: ['JavaScript', 'Python'],
    }

    render(
      <FilterSidebar
        filters={filters}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    const checkbox = screen.getByRole('checkbox', { name: /javascript/i })
    await user.click(checkbox)

    expect(onFilterChange).toHaveBeenCalledWith({
      programming_languages: ['Python'],
    })
  })

  it('shows clear all button when filters are active', () => {
    const onFilterChange = vi.fn()
    const filters: IssueFilters = {
      programming_languages: ['JavaScript'],
    }

    render(
      <FilterSidebar
        filters={filters}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    expect(screen.getByText('Clear all')).toBeInTheDocument()
  })

  it('clears all filters when clear all is clicked', async () => {
    const onFilterChange = vi.fn()
    const user = userEvent.setup()
    
    const filters: IssueFilters = {
      programming_languages: ['JavaScript'],
      labels: ['bug'],
      difficulty_levels: ['easy'],
    }

    render(
      <FilterSidebar
        filters={filters}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    const clearButton = screen.getByText('Clear all')
    await user.click(clearButton)

    expect(onFilterChange).toHaveBeenCalledWith({})
  })

  it('handles null available filters gracefully', () => {
    const onFilterChange = vi.fn()
    render(
      <FilterSidebar
        filters={{}}
        availableFilters={null}
        onFilterChange={onFilterChange}
      />
    )

    expect(screen.getByText('No languages available')).toBeInTheDocument()
    expect(screen.getByText('No labels available')).toBeInTheDocument()
    expect(screen.getByText('No difficulty levels available')).toBeInTheDocument()
  })

  it('checks correct checkboxes based on active filters', () => {
    const onFilterChange = vi.fn()
    const filters: IssueFilters = {
      programming_languages: ['JavaScript'],
      labels: ['bug'],
      difficulty_levels: ['easy'],
    }

    render(
      <FilterSidebar
        filters={filters}
        availableFilters={mockAvailableFilters}
        onFilterChange={onFilterChange}
      />
    )

    const jsCheckbox = screen.getByRole('checkbox', { name: /javascript/i }) as HTMLInputElement
    const bugCheckbox = screen.getByRole('checkbox', { name: /bug/i }) as HTMLInputElement
    const easyCheckbox = screen.getByRole('checkbox', { name: /easy/i }) as HTMLInputElement

    expect(jsCheckbox.checked).toBe(true)
    expect(bugCheckbox.checked).toBe(true)
    expect(easyCheckbox.checked).toBe(true)
  })
})
