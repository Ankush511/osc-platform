'use client'

import { useState } from 'react'
import { RecentContribution } from '@/types/dashboard'

interface ContributionTimelineProps {
  contributions: RecentContribution[]
}

export default function ContributionTimeline({ contributions }: ContributionTimelineProps) {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'merged':
        return 'bg-green-100 text-green-800'
      case 'submitted':
        return 'bg-blue-100 text-blue-800'
      case 'closed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'merged':
        return '✓'
      case 'submitted':
        return '⏳'
      case 'closed':
        return '✕'
      default:
        return '•'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  if (contributions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No contributions yet. Start contributing to earn your first badge!
      </div>
    )
  }

  const filteredContributions = statusFilter === 'all'
    ? contributions
    : contributions.filter(c => c.status === statusFilter)

  return (
    <div>
      {/* Filter Buttons */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setStatusFilter('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            statusFilter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setStatusFilter('merged')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            statusFilter === 'merged'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Merged
        </button>
        <button
          onClick={() => setStatusFilter('submitted')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            statusFilter === 'submitted'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Pending
        </button>
        <button
          onClick={() => setStatusFilter('closed')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            statusFilter === 'closed'
              ? 'bg-gray-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Closed
        </button>
      </div>

      {filteredContributions.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No {statusFilter} contributions found
        </div>
      ) : (
        <div className="flow-root">
          <ul className="-mb-8">
            {filteredContributions.map((contribution, idx) => (
              <li key={contribution.contribution_id}>
                <div className="relative pb-8">
                  {idx !== filteredContributions.length - 1 && (
                    <span
                      className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                      aria-hidden="true"
                    />
                  )}
              <div className="relative flex space-x-3">
                <div>
                  <span
                    className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                      contribution.status === 'merged'
                        ? 'bg-green-500'
                        : contribution.status === 'submitted'
                        ? 'bg-blue-500'
                        : 'bg-gray-400'
                    }`}
                  >
                    <span className="text-white text-sm">
                      {getStatusIcon(contribution.status)}
                    </span>
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {contribution.issue_title}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {contribution.repository}
                    </p>
                    <a
                      href={contribution.pr_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 mt-1 inline-block"
                    >
                      View PR →
                    </a>
                  </div>
                  <div className="whitespace-nowrap text-right text-sm">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        contribution.status
                      )}`}
                    >
                      {contribution.status}
                    </span>
                    <p className="text-gray-500 mt-2">
                      {formatDate(contribution.submitted_at)}
                    </p>
                  </div>
                </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
