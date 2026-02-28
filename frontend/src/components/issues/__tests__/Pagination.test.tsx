import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Pagination from '../Pagination'

describe('Pagination', () => {
  it('renders current page and total pages', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={2} totalPages={10} onPageChange={onPageChange} />)
    
    // Check for page numbers in buttons
    const pageButton = screen.getByRole('button', { name: '2' })
    expect(pageButton).toBeInTheDocument()
    expect(pageButton.className).toContain('bg-blue-600')
  })

  it('disables previous button on first page', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={1} totalPages={10} onPageChange={onPageChange} />)
    
    const prevButtons = screen.getAllByRole('button', { name: /previous/i })
    prevButtons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('disables next button on last page', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={10} totalPages={10} onPageChange={onPageChange} />)
    
    const nextButtons = screen.getAllByRole('button', { name: /next/i })
    nextButtons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })

  it('calls onPageChange with previous page when previous is clicked', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    
    render(<Pagination currentPage={5} totalPages={10} onPageChange={onPageChange} />)
    
    const prevButton = screen.getAllByRole('button', { name: /previous/i })[1]
    await user.click(prevButton)
    
    expect(onPageChange).toHaveBeenCalledWith(4)
  })

  it('calls onPageChange with next page when next is clicked', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    
    render(<Pagination currentPage={5} totalPages={10} onPageChange={onPageChange} />)
    
    const nextButton = screen.getAllByRole('button', { name: /next/i })[1]
    await user.click(nextButton)
    
    expect(onPageChange).toHaveBeenCalledWith(6)
  })

  it('calls onPageChange with specific page when page number is clicked', async () => {
    const onPageChange = vi.fn()
    const user = userEvent.setup()
    
    render(<Pagination currentPage={1} totalPages={10} onPageChange={onPageChange} />)
    
    const pageButton = screen.getByRole('button', { name: '3' })
    await user.click(pageButton)
    
    expect(onPageChange).toHaveBeenCalledWith(3)
  })

  it('highlights current page button', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={3} totalPages={10} onPageChange={onPageChange} />)
    
    const currentPageButton = screen.getByRole('button', { name: '3' })
    expect(currentPageButton.className).toContain('bg-blue-600')
  })

  it('shows ellipsis for large page ranges', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={5} totalPages={20} onPageChange={onPageChange} />)
    
    const ellipses = screen.getAllByText('...')
    expect(ellipses.length).toBeGreaterThan(0)
  })

  it('shows all pages when total pages is small', () => {
    const onPageChange = vi.fn()
    render(<Pagination currentPage={3} totalPages={5} onPageChange={onPageChange} />)
    
    expect(screen.getByRole('button', { name: '1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '2' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '3' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '4' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '5' })).toBeInTheDocument()
  })
})
