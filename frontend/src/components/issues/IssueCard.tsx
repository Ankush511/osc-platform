'use client'

import { Issue } from '@/types/issue'
import Link from 'next/link'

interface IssueCardProps {
  issue: Issue
}

export default function IssueCard({ issue }: IssueCardProps) {
  const getDifficultyColor = (difficulty: string | null) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'hard':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-blue-100 text-blue-800'
      case 'claimed':
        return 'bg-purple-100 text-purple-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'closed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Link href={`/issues/${issue.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6 cursor-pointer">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 flex-1 pr-4 hover:text-blue-600">
            {issue.title}
          </h3>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
              issue.status
            )}`}
          >
            {issue.status}
          </span>
        </div>

        {/* Repository Info */}
        <div className="flex items-center text-sm text-gray-600 mb-3">
          <svg
            className="h-4 w-4 mr-1"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z"
              clipRule="evenodd"
            />
          </svg>
          <span className="font-medium">{issue.repository_full_name || issue.repository_name}</span>
        </div>

        {/* Description */}
        {issue.description && (
          <p className="text-sm text-gray-600 mb-4 line-clamp-2">
            {issue.description}
          </p>
        )}

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Programming Language */}
          {issue.programming_language && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {issue.programming_language}
            </span>
          )}

          {/* Difficulty */}
          {issue.difficulty_level && (
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(
                issue.difficulty_level
              )}`}
            >
              {issue.difficulty_level}
            </span>
          )}

          {/* Labels */}
          {issue.labels.slice(0, 3).map((label) => (
            <span
              key={label}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
            >
              {label}
            </span>
          ))}

          {issue.labels.length > 3 && (
            <span className="text-xs text-gray-500">
              +{issue.labels.length - 3} more
            </span>
          )}
        </div>

        {/* Claimed Info */}
        {issue.status === 'claimed' && issue.claim_expires_at && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">
              Claimed • Expires {new Date(issue.claim_expires_at).toLocaleDateString()}
            </p>
          </div>
        )}
      </div>
    </Link>
  )
}
