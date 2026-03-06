import { describe, it, expect, vi } from 'vitest'
import {
  getErrorDetails,
  logError,
  isRetryableError,
  retryWithBackoff,
} from '../error-handler'
import { APIError } from '../api-client'

describe('getErrorDetails', () => {
  it('should handle API authentication errors', () => {
    const error = new APIError('Unauthorized', 401)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Authentication Required')
    expect(details.canRetry).toBe(false)
  })

  it('should handle API authorization errors', () => {
    const error = new APIError('Forbidden', 403)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Access Denied')
    expect(details.canRetry).toBe(false)
  })

  it('should handle API not found errors', () => {
    const error = new APIError('Not found', 404)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Not Found')
    expect(details.canRetry).toBe(false)
  })

  it('should handle API validation errors', () => {
    const error = new APIError('Validation failed', 422)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Validation Error')
    expect(details.canRetry).toBe(true)
  })

  it('should handle API rate limit errors', () => {
    const error = new APIError('Too many requests', 429)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Too Many Requests')
    expect(details.canRetry).toBe(true)
  })

  it('should handle API server errors', () => {
    const error = new APIError('Internal server error', 500)
    const details = getErrorDetails(error)

    expect(details.title).toBe('Server Error')
    expect(details.canRetry).toBe(true)
  })

  it('should handle network errors', () => {
    const error = new TypeError('Failed to fetch')
    const details = getErrorDetails(error)

    expect(details.title).toBe('Network Error')
    expect(details.canRetry).toBe(true)
  })

  it('should handle generic errors', () => {
    const error = new Error('Something went wrong')
    const details = getErrorDetails(error)

    expect(details.title).toBe('Error')
    expect(details.message).toBe('Something went wrong')
    expect(details.canRetry).toBe(true)
  })

  it('should handle unknown errors', () => {
    const error = 'string error'
    const details = getErrorDetails(error)

    expect(details.title).toBe('Unknown Error')
    expect(details.canRetry).toBe(true)
  })
})

describe('logError', () => {
  it('should log error to console', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const error = new Error('Test error')

    logError(error, { userId: 123 })

    expect(consoleSpy).toHaveBeenCalled()
    consoleSpy.mockRestore()
  })
})

describe('isRetryableError', () => {
  it('should return true for network errors', () => {
    const error = new APIError('Network error', 0)
    expect(isRetryableError(error)).toBe(true)
  })

  it('should return true for rate limit errors', () => {
    const error = new APIError('Too many requests', 429)
    expect(isRetryableError(error)).toBe(true)
  })

  it('should return true for server errors', () => {
    const error = new APIError('Server error', 500)
    expect(isRetryableError(error)).toBe(true)
  })

  it('should return false for client errors', () => {
    const error = new APIError('Bad request', 400)
    expect(isRetryableError(error)).toBe(false)
  })

  it('should return true for fetch errors', () => {
    const error = new TypeError('Failed to fetch')
    expect(isRetryableError(error)).toBe(true)
  })
})

describe('retryWithBackoff', () => {
  it('should succeed on first try', async () => {
    const fn = vi.fn().mockResolvedValue('success')
    const result = await retryWithBackoff(fn, 3, 100)

    expect(result).toBe('success')
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should retry on retryable errors', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new APIError('Server error', 500))
      .mockResolvedValue('success')

    const result = await retryWithBackoff(fn, 3, 100)

    expect(result).toBe('success')
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('should not retry on non-retryable errors', async () => {
    const fn = vi.fn().mockRejectedValue(new APIError('Bad request', 400))

    await expect(retryWithBackoff(fn, 3, 100)).rejects.toThrow()
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('should throw after max retries', async () => {
    const fn = vi.fn().mockRejectedValue(new APIError('Server error', 500))

    await expect(retryWithBackoff(fn, 3, 100)).rejects.toThrow()
    expect(fn).toHaveBeenCalledTimes(3)
  })
})
