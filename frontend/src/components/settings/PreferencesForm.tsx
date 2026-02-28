'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { updateUserPreferences } from '@/lib/users-api'

interface PreferencesFormProps {
  initialLanguages: string[]
  initialLabels: string[]
}

const AVAILABLE_LANGUAGES = [
  'Python',
  'JavaScript',
  'TypeScript',
  'Java',
  'Go',
  'Rust',
  'C++',
  'C#',
  'Ruby',
  'PHP',
  'Swift',
  'Kotlin',
  'Dart',
  'Scala',
  'R',
]

const AVAILABLE_LABELS = [
  'good first issue',
  'beginner-friendly',
  'help wanted',
  'documentation',
  'bug',
  'enhancement',
  'feature',
  'hacktoberfest',
  'easy',
  'medium',
  'hard',
]

export default function PreferencesForm({ initialLanguages, initialLabels }: PreferencesFormProps) {
  const router = useRouter()
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(initialLanguages)
  const [selectedLabels, setSelectedLabels] = useState<string[]>(initialLabels)
  const [customLanguage, setCustomLanguage] = useState('')
  const [customLabel, setCustomLabel] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const toggleLanguage = (language: string) => {
    setSelectedLanguages(prev =>
      prev.includes(language)
        ? prev.filter(l => l !== language)
        : [...prev, language]
    )
  }

  const toggleLabel = (label: string) => {
    setSelectedLabels(prev =>
      prev.includes(label)
        ? prev.filter(l => l !== label)
        : [...prev, label]
    )
  }

  const addCustomLanguage = () => {
    if (customLanguage.trim() && !selectedLanguages.includes(customLanguage.trim())) {
      setSelectedLanguages(prev => [...prev, customLanguage.trim()])
      setCustomLanguage('')
    }
  }

  const addCustomLabel = () => {
    if (customLabel.trim() && !selectedLabels.includes(customLabel.trim())) {
      setSelectedLabels(prev => [...prev, customLabel.trim()])
      setCustomLabel('')
    }
  }

  const removeLanguage = (language: string) => {
    setSelectedLanguages(prev => prev.filter(l => l !== language))
  }

  const removeLabel = (label: string) => {
    setSelectedLabels(prev => prev.filter(l => l !== label))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setSuccess(false)

    try {
      // Get access token from session
      const response = await fetch('/api/auth/session')
      const session = await response.json()

      if (!session?.accessToken) {
        throw new Error('Not authenticated')
      }

      await updateUserPreferences(
        {
          preferred_languages: selectedLanguages,
          preferred_labels: selectedLabels,
        },
        session.accessToken
      )

      setSuccess(true)
      setTimeout(() => {
        router.push('/profile')
        router.refresh()
      }, 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update preferences')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Programming Languages */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Preferred Programming Languages
        </label>
        <p className="text-sm text-gray-500 mb-4">
          Select the programming languages you're interested in or comfortable with
        </p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {AVAILABLE_LANGUAGES.map(language => (
            <button
              key={language}
              type="button"
              onClick={() => toggleLanguage(language)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedLanguages.includes(language)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {language}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={customLanguage}
            onChange={(e) => setCustomLanguage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomLanguage())}
            placeholder="Add custom language"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={addCustomLanguage}
            className="px-4 py-2 bg-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-700"
          >
            Add
          </button>
        </div>

        {selectedLanguages.length > 0 && (
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Selected Languages:</p>
            <div className="flex flex-wrap gap-2">
              {selectedLanguages.map(language => (
                <span
                  key={language}
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                >
                  {language}
                  <button
                    type="button"
                    onClick={() => removeLanguage(language)}
                    className="ml-1 hover:text-blue-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Issue Labels */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Preferred Issue Labels
        </label>
        <p className="text-sm text-gray-500 mb-4">
          Select the types of issues you'd like to work on
        </p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {AVAILABLE_LABELS.map(label => (
            <button
              key={label}
              type="button"
              onClick={() => toggleLabel(label)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedLabels.includes(label)
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={customLabel}
            onChange={(e) => setCustomLabel(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCustomLabel())}
            placeholder="Add custom label"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="button"
            onClick={addCustomLabel}
            className="px-4 py-2 bg-gray-600 text-white rounded-md text-sm font-medium hover:bg-gray-700"
          >
            Add
          </button>
        </div>

        {selectedLabels.length > 0 && (
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Selected Labels:</p>
            <div className="flex flex-wrap gap-2">
              {selectedLabels.map(label => (
                <span
                  key={label}
                  className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                >
                  {label}
                  <button
                    type="button"
                    onClick={() => removeLabel(label)}
                    className="ml-1 hover:text-purple-900"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="rounded-md bg-green-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">Preferences updated successfully!</p>
            </div>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end gap-4">
        <button
          type="button"
          onClick={() => router.back()}
          className="px-6 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </form>
  )
}
