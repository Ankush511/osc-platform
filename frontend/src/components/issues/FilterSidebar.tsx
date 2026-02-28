'use client'

import { IssueFilters, AvailableFilters } from '@/types/issue'

interface FilterSidebarProps {
  filters: IssueFilters
  availableFilters: AvailableFilters | null
  onFilterChange: (filters: IssueFilters) => void
}

export default function FilterSidebar({ 
  filters, 
  availableFilters, 
  onFilterChange 
}: FilterSidebarProps) {
  const toggleLanguage = (language: string) => {
    const current = filters.programming_languages || []
    const updated = current.includes(language)
      ? current.filter(l => l !== language)
      : [...current, language]
    
    onFilterChange({
      ...filters,
      programming_languages: updated.length > 0 ? updated : undefined,
    })
  }

  const toggleLabel = (label: string) => {
    const current = filters.labels || []
    const updated = current.includes(label)
      ? current.filter(l => l !== label)
      : [...current, label]
    
    onFilterChange({
      ...filters,
      labels: updated.length > 0 ? updated : undefined,
    })
  }

  const toggleDifficulty = (difficulty: string) => {
    const current = filters.difficulty_levels || []
    const updated = current.includes(difficulty)
      ? current.filter(d => d !== difficulty)
      : [...current, difficulty]
    
    onFilterChange({
      ...filters,
      difficulty_levels: updated.length > 0 ? updated : undefined,
    })
  }

  const clearFilters = () => {
    onFilterChange({})
  }

  const hasActiveFilters = 
    (filters.programming_languages?.length || 0) > 0 ||
    (filters.labels?.length || 0) > 0 ||
    (filters.difficulty_levels?.length || 0) > 0

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Programming Languages */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          Programming Language
        </h4>
        <div className="space-y-2">
          {availableFilters?.programming_languages?.map((language) => (
            <label key={language} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.programming_languages?.includes(language) || false}
                onChange={() => toggleLanguage(language)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">{language}</span>
            </label>
          ))}
          {(!availableFilters?.programming_languages || 
            availableFilters.programming_languages.length === 0) && (
            <p className="text-sm text-gray-500">No languages available</p>
          )}
        </div>
      </div>

      {/* Labels */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Labels</h4>
        <div className="space-y-2">
          {availableFilters?.labels?.map((label) => (
            <label key={label} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.labels?.includes(label) || false}
                onChange={() => toggleLabel(label)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700">{label}</span>
            </label>
          ))}
          {(!availableFilters?.labels || availableFilters.labels.length === 0) && (
            <p className="text-sm text-gray-500">No labels available</p>
          )}
        </div>
      </div>

      {/* Difficulty */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-3">Difficulty</h4>
        <div className="space-y-2">
          {availableFilters?.difficulty_levels?.map((difficulty) => (
            <label key={difficulty} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.difficulty_levels?.includes(difficulty) || false}
                onChange={() => toggleDifficulty(difficulty)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-700 capitalize">
                {difficulty}
              </span>
            </label>
          ))}
          {(!availableFilters?.difficulty_levels || 
            availableFilters.difficulty_levels.length === 0) && (
            <p className="text-sm text-gray-500">No difficulty levels available</p>
          )}
        </div>
      </div>
    </div>
  )
}
