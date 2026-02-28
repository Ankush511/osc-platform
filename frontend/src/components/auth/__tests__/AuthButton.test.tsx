import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { AuthButton } from '../AuthButton'

// Mock the auth context
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}))

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

describe('AuthButton', () => {
  const mockPush = vi.fn()
  const mockSignOut = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useRouter).mockReturnValue({
      push: mockPush,
      replace: vi.fn(),
      prefetch: vi.fn(),
      back: vi.fn(),
    } as any)
  })

  it('should show loading state', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    // Check for loading skeleton
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('should show sign in button when not authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    const signInButton = screen.getByRole('button', { name: /sign in/i })
    expect(signInButton).toBeInTheDocument()
  })

  it('should navigate to signin page when sign in clicked', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    const signInButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(signInButton)

    expect(mockPush).toHaveBeenCalledWith('/auth/signin')
  })

  it('should show user info and sign out button when authenticated', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: '1',
        name: 'Test User',
        email: 'test@example.com',
        image: 'https://example.com/avatar.jpg',
      },
      accessToken: 'mock-token',
      isAuthenticated: true,
      isLoading: false,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /test user/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument()
  })

  it('should call signOut when sign out button clicked', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: '1',
        name: 'Test User',
        email: 'test@example.com',
      },
      accessToken: 'mock-token',
      isAuthenticated: true,
      isLoading: false,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    fireEvent.click(signOutButton)

    expect(mockSignOut).toHaveBeenCalled()
  })

  it('should display email when name is not available', () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: '1',
        email: 'test@example.com',
      },
      accessToken: 'mock-token',
      isAuthenticated: true,
      isLoading: false,
      signOut: mockSignOut,
      refreshSession: vi.fn(),
    })

    render(<AuthButton />)

    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })
})
