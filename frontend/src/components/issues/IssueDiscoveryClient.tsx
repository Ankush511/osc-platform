'use client'

import { useState, useEffect, useCallback } from 'react'
import { IssueFilters, AvailableFilters, PaginatedIssuesResponse } from '@/types/issue'
import { fetchIssues } from '@/lib/issues-api'
import IssueList from './IssueList'
import FilterSidebar from './FilterSidebar'
import SearchBar from './SearchBar'

interface IssueDiscoveryClientProps {
  accessToken: string
  availableFilters: AvailableFilters | null
}

export default function IssueDiscoveryClient({ 
  accessToken, 
  availableFilters 
}: IssueDiscoveryClientProps) {
  const [filters, setFilters] = useState<IssueFilters>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [issuesData, setIssuesData] = useState<PaginatedIssuesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const loadIssues = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await fetchIssues({
        page,
        page_size: 20,
        filters: {
          ...filters,
          search_query: searchQuery || undefined,
        },
        accessToken,
      })
      setIssuesData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load issues')
    } finally {
      setLoading(false)
    }
  }, [page, filters, searchQuery, accessToken])

  useEffect(() => {
    loadIssues()
  }, [loadIssues])

  const handleFilterChange = (newFilters: IssueFilters) => {
    setFilters(newFilters)
    setPage(1) // Reset to first page when filters change
  }

  const handleSearchChange = (query: string) => {
    setSearchQuery(query)
    setPage(1) // Reset to first page when search changes
  }

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900">
          Discover Open Source Issues
        </h2>
        <p className="mt-2 text-gray-600">
          Find beginner-friendly issues to start your open source journey
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <SearchBar 
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      {/* Mobile Filter Toggle */}
      <div className="lg:hidden mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          {showFilters ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Filter Sidebar */}
        <aside className={`lg:block ${showFilters ? 'block' : 'hidden'} lg:w-64 flex-shrink-0`}>
          <FilterSidebar
            filters={filters}
            availableFilters={availableFilters}
            onFilterChange={handleFilterChange}
          />
        </aside>

        {/* Issue List */}
        <div className="flex-1">
          <IssueList
            issuesData={issuesData}
            loading={loading}
            error={error}
            currentPage={page}
            onPageChange={handlePageChange}
          />
        </div>
      </div>
    </div>
  )
}
