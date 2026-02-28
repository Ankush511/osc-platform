'use client'

import { Contribution } from '@/types/contribution'

interface PRStatusDisplayProps {
  contribution: Contribution
}

export default function PRStatusDisplay({ contribution }: PRStatusDisplayProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'merged':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'submitted':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'merged':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        )
      case 'submitted':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clipRule="evenodd"
            />
          </svg>
        )
      case 'closed':
        return (
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        )
      default:
        return null
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'merged':
        return 'Merged'
      case 'submitted':
        return 'Pending Review'
      case 'closed':
        return 'Closed'
      default:
        return status
    }
  }

  const getStatusDescription = (status: string) => {
    switch (status) {
      case 'merged':
        return 'Your pull request has been merged! Great work!'
      case 'submitted':
        return 'Your pull request is under review. Check back for updates.'
      case 'closed':
        return 'This pull request was closed without merging.'
      default:
        return ''
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor(contribution.status)}`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">{getStatusIcon(contribution.status)}</div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-sm font-semibold">
              {getStatusText(contribution.status)}
            </h3>
            <span className="text-xs font-medium px-2 py-0.5 bg-white bg-opacity-50 rounded">
              +{contribution.points_earned} points
            </span>
          </div>
          
          <p className="text-sm mb-2">{getStatusDescription(contribution.status)}</p>
          
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-medium">PR #{contribution.pr_number}</span>
              <span className="text-gray-600">•</span>
              <a
                href={contribution.pr_url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline flex items-center gap-1"
              >
                View on GitHub
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                  <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                </svg>
              </a>
            </div>
            
            <div className="text-gray-600">
              Submitted: {formatDate(contribution.submitted_at)}
            </div>
            
            {contribution.merged_at && (
              <div className="text-gray-600">
                Merged: {formatDate(contribution.merged_at)}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
