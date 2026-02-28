import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../AuthContext'
import { SessionProvider } from 'next-auth/react'
import { ReactNode } from 'react'

// Mock useSession
vi.mock('next-auth/react', async () => {
  const actual = await vi.importActual('next-auth/react')
  return {
    ...actual,
    useSession: vi.fn(),
    signOut: vi.fn(),
  }
})

import { useSession, signOut } from 'next-auth/react'

const wrapper = ({ children }: { children: ReactNode }) => (
  <SessionProvider session={null}>
    <AuthProvider>{children}</AuthProvider>
  </SessionProvider>
)

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should provide authenticated user data', () => {
    vi.mocked(useSession).mockReturnValue({
      data: {
        user: { id: '1', name: 'Test User', email: 'test@example.com' },
        accessToken: 'mock-token',
        expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
      status: 'authenticated',
      update: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.name).toBe('Test User')
    expect(result.current.accessToken).toBe('mock-token')
  })

  it('should handle unauthenticated state', () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      status: 'unauthenticated',
      update: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
    expect(result.current.accessToken).toBeNull()
  })

  it('should handle loading state', () => {
    vi.mocked(useSession).mockReturnValue({
      data: null,
      status: 'loading',
      update: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.isLoading).toBe(true)
  })

  it('should call signOut when signOut is invoked', async () => {
    vi.mocked(useSession).mockReturnValue({
      data: {
        user: { id: '1', name: 'Test User' },
        accessToken: 'mock-token',
        expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      },
      status: 'authenticated',
      update: vi.fn(),
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await result.current.signOut()

    expect(signOut).toHaveBeenCalledWith({ callbackUrl: '/' })
  })

  it('should throw error when used outside AuthProvider', () => {
    expect(() => {
      renderHook(() => useAuth())
    }).toThrow('useAuth must be used within an AuthProvider')
  })
})
