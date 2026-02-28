'use client'

import { useState, useEffect } from 'react'
import { getUserContributions } from '@/lib/contributions-api'
import { Contribution } from '@/types/contribution'
import PRStatusDisplay from './PRStatusDisplay'

interface PRManagementProps {
  userId: number
  issueId: number
  accessToken: string
}

export default function PRManagement({
  userId,
  issueId,
  accessToken,
}: PRManagementProps) {
  const [contribution, setContribution] = useState<Contribution | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadContribution()
  }, [issueId, userId])

  const loadContribution = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const contributions = await getUserContributions(userId, accessToken)
      
      // Find contribution for this specific issue
      const issueContribution = contributions.find(c => c.issue_id === issueId)
      
      if (issueContribution) {
        setContribution(issueContribution)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load contribution')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-center py-8">
          <svg
            className="animate-spin h-8 w-8 text-blue-600"
            viewBox="0 0 24 24"
          >
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
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="text-center py-4">
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadContribution}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!contribution) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Your Contribution
      </h3>
      <PRStatusDisplay contribution={contribution} />
    </div>
  )
}
