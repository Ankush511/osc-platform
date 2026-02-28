'use client'

import { PaginatedIssuesResponse } from '@/types/issue'
import IssueCard from './IssueCard'
import Pagination from './Pagination'

interface IssueListProps {
  issuesData: PaginatedIssuesResponse | null
  loading: boolean
  error: string | null
  currentPage: number
  onPageChange: (page: number) => void
}

export default function IssueList({
  issuesData,
  loading,
  error,
  currentPage,
  onPageChange,
}: IssueListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-lg shadow p-6 animate-pulse"
          >
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <svg
          className="mx-auto h-12 w-12 text-red-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <h3 className="text-lg font-medium text-red-900 mb-2">
          Error Loading Issues
        </h3>
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  if (!issuesData || issuesData.items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No Issues Found
        </h3>
        <p className="text-gray-600">
          Try adjusting your filters or search query
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {issuesData.items.length} of {issuesData.total} issues
      </div>

      {/* Issue Cards */}
      <div className="space-y-4 mb-6">
        {issuesData.items.map((issue) => (
          <IssueCard key={issue.id} issue={issue} />
        ))}
      </div>

      {/* Pagination */}
      {issuesData.total_pages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={issuesData.total_pages}
          onPageChange={onPageChange}
        />
      )}
    </div>
  )
}
