import { APIError } from './api-client'

export interface ErrorDetails {
  title: string
  message: string
  action?: string
  canRetry: boolean
}

/**
 * Get user-friendly error details from an error object.
 */
export function getErrorDetails(error: unknown): ErrorDetails {
  // Handle API errors
  if (error instanceof APIError) {
    return handleAPIError(error)
  }

  // Handle network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      title: 'Network Error',
      message: 'Unable to connect to the server. Please check your internet connection.',
      action: 'Check your connection and try again',
      canRetry: true,
    }
  }

  // Handle generic errors
  if (error instanceof Error) {
    return {
      title: 'Error',
      message: error.message || 'An unexpected error occurred',
      canRetry: true,
    }
  }

  // Unknown error
  return {
    title: 'Unknown Error',
    message: 'An unexpected error occurred. Please try again.',
    canRetry: true,
  }
}

/**
 * Handle API-specific errors with appropriate messages.
 */
function handleAPIError(error: APIError): ErrorDetails {
  const { status, code, message } = error

  // Authentication errors
  if (status === 401) {
    return {
      title: 'Authentication Required',
      message: 'Please sign in to continue',
      action: 'Sign in',
      canRetry: false,
    }
  }

  // Authorization errors
  if (status === 403) {
    return {
      title: 'Access Denied',
      message: 'You do not have permission to perform this action',
      canRetry: false,
    }
  }

  // Not found errors
  if (status === 404) {
    return {
      title: 'Not Found',
      message: 'The requested resource could not be found',
      canRetry: false,
    }
  }

  // Validation errors
  if (status === 422) {
    return {
      title: 'Validation Error',
      message: message || 'Please check your input and try again',
      canRetry: true,
    }
  }

  // Rate limiting
  if (status === 429) {
    return {
      title: 'Too Many Requests',
      message: 'You have made too many requests. Please wait a moment and try again.',
      action: 'Wait and retry',
      canRetry: true,
    }
  }

  // Server errors
  if (status >= 500) {
    return {
      title: 'Server Error',
      message: 'Our servers are experiencing issues. Please try again later.',
      action: 'Try again later',
      canRetry: true,
    }
  }

  // External service errors
  if (code === 'EXTERNAL_SERVICE_ERROR') {
    return {
      title: 'Service Unavailable',
      message: 'An external service is temporarily unavailable. Please try again later.',
      canRetry: true,
    }
  }

  // Default error
  return {
    title: 'Error',
    message: message || 'An error occurred. Please try again.',
    canRetry: true,
  }
}

/**
 * Log error to console (and potentially to error tracking service).
 */
export function logError(error: unknown, context?: Record<string, any>) {
  console.error('Error occurred:', {
    error,
    context,
    timestamp: new Date().toISOString(),
  })

  // In production, send to error tracking service (e.g., Sentry)
  if (process.env.NODE_ENV === 'production') {
    // TODO: Integrate with error tracking service
    // Sentry.captureException(error, { extra: context })
  }
}

/**
 * Check if an error is retryable.
 */
export function isRetryableError(error: unknown): boolean {
  if (error instanceof APIError) {
    // Retry on network errors, rate limits, and server errors
    return error.status === 0 || error.status === 429 || error.status >= 500
  }

  // Retry on network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true
  }

  return false
}

/**
 * Retry a function with exponential backoff.
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: unknown

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry if error is not retryable
      if (!isRetryableError(error)) {
        throw error
      }

      // Don't wait after last attempt
      if (attempt < maxRetries - 1) {
        const delay = initialDelay * Math.pow(2, attempt)
        await new Promise((resolve) => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError
}
