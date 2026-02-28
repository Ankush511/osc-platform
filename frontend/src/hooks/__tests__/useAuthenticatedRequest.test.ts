import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useAuthenticatedRequest } from '../useAuthenticatedRequest'
import { APIError } from '@/lib/api-client'

// Mock the auth context
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: vi.fn(),
}))

// Mock the api client
vi.mock('@/lib/api-client', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
  APIError: class APIError extends Error {
    constructor(message: string, public status: number) {
      super(message)
      this.name = 'APIError'
    }
  },
}))

import { useAuth } from '@/contexts/AuthContext'
import { api } from '@/lib/api-client'

describe('useAuthenticatedRequest', () => {
  const mockSignOut = vi.fn()
  const mockRefreshSession = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useAuth).mockReturnValue({
      accessToken: 'mock-token',
      signOut: mockSignOut,
      refreshSession: mockRefreshSession,
      user: null,
      isAuthenticated: true,
      isLoading: false,
    })
  })

  it('should make successful GET request', async () => {
    const mockData = { id: 1, name: 'Test' }
    vi.mocked(api.get).mockResolvedValueOnce(mockData)

    const { result } = renderHook(() => useAuthenticatedRequest())
    const data = await result.current.get('/test')

    expect(api.get).toHaveBeenCalledWith('/test', 'mock-token')
    expect(data).toEqual(mockData)
  })

  it('should make successful POST request', async () => {
    const postData = { name: 'New Item' }
    const mockResponse = { id: 1, ...postData }
    vi.mocked(api.post).mockResolvedValueOnce(mockResponse)

    const { result } = renderHook(() => useAuthenticatedRequest())
    const data = await result.current.post('/items', postData)

    expect(api.post).toHaveBeenCalledWith('/items', postData, 'mock-token')
    expect(data).toEqual(mockResponse)
  })

  it('should handle 401 error and retry after refresh', async () => {
    const mockData = { success: true }
    
    // First call fails with 401
    vi.mocked(api.get)
      .mockRejectedValueOnce(new APIError('Unauthorized', 401))
      .mockResolvedValueOnce(mockData)

    mockRefreshSession.mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useAuthenticatedRequest())
    const data = await result.current.get('/protected')

    expect(mockRefreshSession).toHaveBeenCalled()
    expect(api.get).toHaveBeenCalledTimes(2)
    expect(data).toEqual(mockData)
  })

  it('should sign out if refresh fails', async () => {
    vi.mocked(api.get).mockRejectedValueOnce(new APIError('Unauthorized', 401))
    mockRefreshSession.mockRejectedValueOnce(new Error('Refresh failed'))

    const { result } = renderHook(() => useAuthenticatedRequest())

    await expect(result.current.get('/protected')).rejects.toThrow(
      'Session expired. Please sign in again.'
    )

    expect(mockSignOut).toHaveBeenCalled()
  })

  it('should throw error if no access token', async () => {
    vi.mocked(useAuth).mockReturnValue({
      accessToken: null,
      signOut: mockSignOut,
      refreshSession: mockRefreshSession,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })

    const { result } = renderHook(() => useAuthenticatedRequest())

    await expect(result.current.get('/test')).rejects.toThrow(
      'No access token available'
    )
  })

  it('should handle non-401 API errors', async () => {
    const error = new APIError('Not found', 404)
    vi.mocked(api.get).mockRejectedValueOnce(error)

    const { result } = renderHook(() => useAuthenticatedRequest())

    await expect(result.current.get('/not-found')).rejects.toThrow(error)
    expect(mockRefreshSession).not.toHaveBeenCalled()
    expect(mockSignOut).not.toHaveBeenCalled()
  })

  it('should support PUT requests', async () => {
    const updateData = { name: 'Updated' }
    vi.mocked(api.put).mockResolvedValueOnce(updateData)

    const { result } = renderHook(() => useAuthenticatedRequest())
    await result.current.put('/items/1', updateData)

    expect(api.put).toHaveBeenCalledWith('/items/1', updateData, 'mock-token')
  })

  it('should support PATCH requests', async () => {
    const patchData = { status: 'active' }
    vi.mocked(api.patch).mockResolvedValueOnce(patchData)

    const { result } = renderHook(() => useAuthenticatedRequest())
    await result.current.patch('/items/1', patchData)

    expect(api.patch).toHaveBeenCalledWith('/items/1', patchData, 'mock-token')
  })

  it('should support DELETE requests', async () => {
    vi.mocked(api.delete).mockResolvedValueOnce({})

    const { result } = renderHook(() => useAuthenticatedRequest())
    await result.current.delete('/items/1')

    expect(api.delete).toHaveBeenCalledWith('/items/1', 'mock-token')
  })
})
