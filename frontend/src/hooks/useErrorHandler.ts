import { useState, useCallback } from 'react'
import { getErrorDetails, logError, ErrorDetails } from '@/lib/error-handler'

interface UseErrorHandlerReturn {
  error: ErrorDetails | null
  setError: (error: unknown) => void
  clearError: () => void
  handleError: (error: unknown, context?: Record<string, any>) => void
}

/**
 * Hook for handling errors with user-friendly messages.
 */
export function useErrorHandler(): UseErrorHandlerReturn {
  const [error, setErrorState] = useState<ErrorDetails | null>(null)

  const setError = useCallback((error: unknown) => {
    const details = getErrorDetails(error)
    setErrorState(details)
  }, [])

  const clearError = useCallback(() => {
    setErrorState(null)
  }, [])

  const handleError = useCallback((error: unknown, context?: Record<string, any>) => {
    // Log error
    logError(error, context)

    // Set error state
    setError(error)
  }, [setError])

  return {
    error,
    setError,
    clearError,
    handleError,
  }
}
