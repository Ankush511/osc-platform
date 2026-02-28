import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useErrorHandler } from '../useErrorHandler'
import { APIError } from '@/lib/api-client'

describe('useErrorHandler', () => {
  it('should initialize with no error', () => {
    const { result } = renderHook(() => useErrorHandler())

    expect(result.current.error).toBeNull()
  })

  it('should set error from Error object', () => {
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.setError(new Error('Test error'))
    })

    expect(result.current.error).not.toBeNull()
    expect(result.current.error?.message).toBe('Test error')
  })

  it('should set error from APIError', () => {
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.setError(new APIError('Unauthorized', 401))
    })

    expect(result.current.error).not.toBeNull()
    expect(result.current.error?.title).toBe('Authentication Required')
  })

  it('should clear error', () => {
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.setError(new Error('Test error'))
    })

    expect(result.current.error).not.toBeNull()

    act(() => {
      result.current.clearError()
    })

    expect(result.current.error).toBeNull()
  })

  it('should handle error with context', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const { result } = renderHook(() => useErrorHandler())

    act(() => {
      result.current.handleError(new Error('Test error'), { userId: 123 })
    })

    expect(result.current.error).not.toBeNull()
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })
})
