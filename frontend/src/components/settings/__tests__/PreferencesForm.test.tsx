import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import PreferencesForm from '../PreferencesForm'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    back: vi.fn(),
    refresh: vi.fn(),
  }),
}))

// Mock fetch
global.fetch = vi.fn()

describe('PreferencesForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with initial languages and labels', () => {
    render(
      <PreferencesForm
        initialLanguages={['Python', 'JavaScript']}
        initialLabels={['good first issue', 'bug']}
      />
    )
    
    expect(screen.getByText('Preferred Programming Languages')).toBeInTheDocument()
    expect(screen.getByText('Preferred Issue Labels')).toBeInTheDocument()
  })

  it('displays selected languages', () => {
    render(
      <PreferencesForm
        initialLanguages={['Python', 'JavaScript']}
        initialLabels={[]}
      />
    )
    
    const selectedSection = screen.getByText('Selected Languages:')
    expect(selectedSection).toBeInTheDocument()
    
    // Check that Python appears in the selected section
    const selectedLanguages = screen.getByText('Selected Languages:').parentElement
    expect(selectedLanguages?.textContent).toContain('Python')
  })

  it('displays selected labels', () => {
    render(
      <PreferencesForm
        initialLanguages={[]}
        initialLabels={['good first issue', 'bug']}
      />
    )
    
    const selectedSection = screen.getByText('Selected Labels:')
    expect(selectedSection).toBeInTheDocument()
  })

  it('toggles language selection', () => {
    render(
      <PreferencesForm
        initialLanguages={[]}
        initialLabels={[]}
      />
    )
    
    const pythonButton = screen.getAllByText('Python').find(el => 
      el.tagName === 'BUTTON'
    )
    
    fireEvent.click(pythonButton!)
    
    expect(screen.getByText('Selected Languages:')).toBeInTheDocument()
  })

  it('toggles label selection', () => {
    render(
      <PreferencesForm
        initialLanguages={[]}
        initialLabels={[]}
      />
    )
    
    const bugButton = screen.getAllByText('bug').find(el => 
      el.tagName === 'BUTTON'
    )
    
    fireEvent.click(bugButton!)
    
    expect(screen.getByText('Selected Labels:')).toBeInTheDocument()
  })

  it('adds custom language', () => {
    render(
      <PreferencesForm
        initialLanguages={[]}
        initialLabels={[]}
      />
    )
    
    const languageInput = screen.getByPlaceholderText('Add custom language')
    const addButton = screen.getAllByText('Add')[0]
    
    fireEvent.change(languageInput, { target: { value: 'Elixir' } })
    fireEvent.click(addButton)
    
    expect(screen.getByText('Selected Languages:')).toBeInTheDocument()
  })

  it('adds custom label', () => {
    render(
      <PreferencesForm
        initialLanguages={[]}
        initialLabels={[]}
      />
    )
    
    const labelInput = screen.getByPlaceholderText('Add custom label')
    const addButtons = screen.getAllByText('Add')
    const addLabelButton = addButtons[1]
    
    fireEvent.change(labelInput, { target: { value: 'custom-label' } })
    fireEvent.click(addLabelButton)
    
    expect(screen.getByText('Selected Labels:')).toBeInTheDocument()
  })

  it('removes selected language', () => {
    render(
      <PreferencesForm
        initialLanguages={['Python']}
        initialLabels={[]}
      />
    )
    
    const removeButton = screen.getByText('×')
    fireEvent.click(removeButton)
    
    expect(screen.queryByText('Selected Languages:')).not.toBeInTheDocument()
  })

  it('submits form successfully', async () => {
    const mockSession = { accessToken: 'test-token' }
    const mockResponse = { ok: true, json: async () => mockSession }
    
    ;(global.fetch as any).mockResolvedValueOnce(mockResponse)
    ;(global.fetch as any).mockResolvedValueOnce({ ok: true, json: async () => ({}) })
    
    render(
      <PreferencesForm
        initialLanguages={['Python']}
        initialLabels={['bug']}
      />
    )
    
    const submitButton = screen.getByText('Save Preferences')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Preferences updated successfully!')).toBeInTheDocument()
    })
  })

  it('displays error on submission failure', async () => {
    const mockSession = { accessToken: 'test-token' }
    const mockResponse = { ok: true, json: async () => mockSession }
    
    ;(global.fetch as any).mockResolvedValueOnce(mockResponse)
    ;(global.fetch as any).mockResolvedValueOnce({ ok: false })
    
    render(
      <PreferencesForm
        initialLanguages={['Python']}
        initialLabels={['bug']}
      />
    )
    
    const submitButton = screen.getByText('Save Preferences')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to update preferences/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while loading', async () => {
    const mockSession = { accessToken: 'test-token' }
    const mockResponse = { ok: true, json: async () => mockSession }
    
    ;(global.fetch as any).mockResolvedValueOnce(mockResponse)
    ;(global.fetch as any).mockImplementation(() => new Promise(() => {}))
    
    render(
      <PreferencesForm
        initialLanguages={['Python']}
        initialLabels={['bug']}
      />
    )
    
    const submitButton = screen.getByText('Save Preferences')
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })
  })
})
