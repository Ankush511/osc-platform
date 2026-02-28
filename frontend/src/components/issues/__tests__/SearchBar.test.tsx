import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchBar from '../SearchBar'

describe('SearchBar', () => {
  it('renders search input with placeholder', () => {
    const onChange = vi.fn()
    render(<SearchBar value="" onChange={onChange} />)
    
    expect(screen.getByPlaceholderText(/search issues/i)).toBeInTheDocument()
  })

  it('displays the provided value', () => {
    const onChange = vi.fn()
    render(<SearchBar value="test query" onChange={onChange} />)
    
    const input = screen.getByPlaceholderText(/search issues/i) as HTMLInputElement
    expect(input.value).toBe('test query')
  })

  it('debounces onChange calls', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    
    render(<SearchBar value="" onChange={onChange} debounceMs={300} />)
    
    const input = screen.getByPlaceholderText(/search issues/i)
    
    await user.type(input, 'test')
    
    expect(onChange).not.toHaveBeenCalled()
    
    await waitFor(() => {
      expect(onChange).toHaveBeenCalledWith('test')
    }, { timeout: 1000 })
  })

  it('clears input when clear button is clicked', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    
    render(<SearchBar value="test query" onChange={onChange} />)
    
    const clearButton = screen.getByRole('button')
    await user.click(clearButton)
    
    expect(onChange).toHaveBeenCalledWith('')
  })

  it('shows clear button only when input has value', () => {
    const onChange = vi.fn()
    const { rerender } = render(<SearchBar value="" onChange={onChange} />)
    
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    
    rerender(<SearchBar value="test" onChange={onChange} />)
    
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('updates local value immediately on typing', async () => {
    const onChange = vi.fn()
    const user = userEvent.setup()
    
    render(<SearchBar value="" onChange={onChange} />)
    
    const input = screen.getByPlaceholderText(/search issues/i) as HTMLInputElement
    
    await user.type(input, 'new')
    
    expect(input.value).toBe('new')
  })
})
