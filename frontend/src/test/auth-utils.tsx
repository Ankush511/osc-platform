import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { AuthProvider } from '@/contexts/AuthContext'

interface MockSession {
  user?: {
    id?: string
    name?: string | null
    email?: string | null
    image?: string | null
  }
  accessToken?: string
  expires?: string
}

export function createMockSession(overrides?: Partial<MockSession>): MockSession {
  return {
    user: {
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
      image: 'https://example.com/avatar.jpg',
      ...overrides?.user,
    },
    accessToken: 'mock-access-token',
    expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    ...overrides,
  }
}

interface AuthWrapperProps {
  children: ReactNode
  session?: MockSession | null
}

export function AuthWrapper({ children, session = createMockSession() }: AuthWrapperProps) {
  return (
    <SessionProvider session={session}>
      <AuthProvider>{children}</AuthProvider>
    </SessionProvider>
  )
}

export function mockFetch(response: any, status = 200) {
  return vi.fn(() =>
    Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      json: () => Promise.resolve(response),
      text: () => Promise.resolve(JSON.stringify(response)),
    })
  ) as any
}
