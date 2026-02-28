'use client'

import { useState } from 'react'
import { submitPullRequest } from '@/lib/contributions-api'
import { SubmissionResult } from '@/types/contribution'

interface PRSubmissionFormProps {
  issueId: number
  userId: number
  accessToken: string
  onSuccess: (result: SubmissionResult) => void
  onCancel?: () => void
}

export default function PRSubmissionForm({
  issueId,
  userId,
  accessToken,
  onSuccess,
  onCancel,
}: PRSubmissionFormProps) {
  const [prUrl, setPrUrl] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  const validatePRUrl = (url: string): string[] => {
    const errors: string[] = []

    if (!url.trim()) {
      errors.push('PR URL is required')
      return errors
    }

    // Check if it's a valid URL
    try {
      const urlObj = new URL(url)
      
      // Check if it's a GitHub URL
      if (!urlObj.hostname.includes('github.com')) {
        errors.push('URL must be from github.com')
      }

      // Check if it's a pull request URL
      if (!url.includes('/pull/')) {
        errors.push('URL must be a GitHub pull request (should contain /pull/)')
      }
    } catch {
      errors.push('Invalid URL format')
    }

    return errors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate URL
    const errors = validatePRUrl(prUrl)
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }

    setIsSubmitting(true)
    setError(null)
    setValidationErrors([])

    try {
      const result = await submitPullRequest(issueId, prUrl, userId, accessToken)
      
      if (result.success) {
        onSuccess(result)
      } else {
        setError(result.message)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit pull request')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleButtonClick = () => {
    // Show validation errors even when button is disabled
    if (!prUrl.trim()) {
      setValidationErrors(['PR URL is required'])
    }
  }

  const handleUrlChange = (value: string) => {
    setPrUrl(value)
    // Clear validation errors when user starts typing
    if (validationErrors.length > 0) {
      setValidationErrors([])
    }
    if (error) {
      setError(null)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="pr-url" className="block text-sm font-medium text-gray-700 mb-2">
          Pull Request URL
        </label>
        <input
          id="pr-url"
          type="text"
          value={prUrl}
          onChange={(e) => handleUrlChange(e.target.value)}
          placeholder="https://github.com/owner/repo/pull/123"
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            validationErrors.length > 0 || error
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300'
          }`}
          disabled={isSubmitting}
        />
        
        {validationErrors.length > 0 && (
          <div className="mt-2 space-y-1">
            {validationErrors.map((err, index) => (
              <p key={index} className="text-sm text-red-600 flex items-center gap-1">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                {err}
              </p>
            ))}
          </div>
        )}

        {error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700 flex items-start gap-2">
              <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span>{error}</span>
            </p>
          </div>
        )}

        <p className="mt-2 text-sm text-gray-500">
          Enter the URL of your pull request. We'll verify it's linked to this issue and created by you.
        </p>
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          onClick={handleButtonClick}
          disabled={isSubmitting}
          className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Validating...
            </span>
          ) : (
            'Submit Pull Request'
          )}
        </button>
        
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
