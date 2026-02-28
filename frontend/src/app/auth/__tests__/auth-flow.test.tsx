import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import SignInPage from '../signin/page'
import AuthErrorPage from '../error/page'

// Mock next-auth
vi.mock('@/auth', () => ({
  signIn: vi.fn(),
}))

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useSearchParams: vi.fn(),
}))

import { useSearchParams } from 'next/navigation'

describe('Authentication Flow', () => {
  describe('SignInPage', () => {
    it('should render sign in page with GitHub button', () => {
      render(<SignInPage />)

      expect(screen.getByText('Welcome to OSCP')).toBeInTheDocument()
      expect(screen.getByText('Sign in with your GitHub account to get started')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in with github/i })).toBeInTheDocument()
    })

    it('should display terms and privacy policy notice', () => {
      render(<SignInPage />)

      expect(screen.getByText(/by signing in, you agree to our terms of service and privacy policy/i)).toBeInTheDocument()
    })
  })

  describe('AuthErrorPage', () => {
    beforeEach(() => {
      vi.clearAllMocks()
    })

    it('should display default error message when no error param', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue(null),
      } as any)

      render(<AuthErrorPage />)

      expect(screen.getByText('Authentication Error')).toBeInTheDocument()
      expect(screen.getByText('An error occurred during authentication.')).toBeInTheDocument()
    })

    it('should display configuration error message', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue('Configuration'),
      } as any)

      render(<AuthErrorPage />)

      expect(screen.getByText('There is a problem with the server configuration.')).toBeInTheDocument()
    })

    it('should display access denied error message', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue('AccessDenied'),
      } as any)

      render(<AuthErrorPage />)

      expect(screen.getByText('You do not have permission to sign in.')).toBeInTheDocument()
    })

    it('should display backend auth error message', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue('BackendAuthError'),
      } as any)

      render(<AuthErrorPage />)

      expect(screen.getByText('Failed to authenticate with the backend server. Please try again.')).toBeInTheDocument()
    })

    it('should display refresh token error message', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue('RefreshTokenError'),
      } as any)

      render(<AuthErrorPage />)

      expect(screen.getByText('Your session has expired. Please sign in again.')).toBeInTheDocument()
    })

    it('should have try again button linking to signin', () => {
      vi.mocked(useSearchParams).mockReturnValue({
        get: vi.fn().mockReturnValue(null),
      } as any)

      render(<AuthErrorPage />)

      const tryAgainLink = screen.getByRole('link', { name: /try again/i })
      expect(tryAgainLink).toHaveAttribute('href', '/auth/signin')
    })
  })
})
