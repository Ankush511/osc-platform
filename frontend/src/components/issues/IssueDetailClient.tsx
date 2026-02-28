'use client'

import { useState } from 'react'
import { Issue } from '@/types/issue'
import { IssueExplanationResponse, RepositorySummaryResponse } from '@/types/ai'
import { SubmissionResult } from '@/types/contribution'
import CountdownTimer from './CountdownTimer'
import { claimIssue, releaseIssue, extendClaimDeadline } from '@/lib/issues-api'
import { useRouter } from 'next/navigation'
import PRSubmissionForm from './PRSubmissionForm'
import PRManagement from './PRManagement'
import ContributionCelebration from './ContributionCelebration'

interface IssueDetailClientProps {
  issue: Issue
  repositorySummary: RepositorySummaryResponse | null
  issueExplanation: IssueExplanationResponse | null
  accessToken: string
  currentUserId: number
}

export default function IssueDetailClient({
  issue: initialIssue,
  repositorySummary,
  issueExplanation,
  accessToken,
  currentUserId,
}: IssueDetailClientProps) {
  const router = useRouter()
  const [issue, setIssue] = useState(initialIssue)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showExtendModal, setShowExtendModal] = useState(false)
  const [extensionDays, setExtensionDays] = useState(7)
  const [justification, setJustification] = useState('')
  const [showPRForm, setShowPRForm] = useState(false)
  const [celebrationResult, setCelebrationResult] = useState<SubmissionResult | null>(null)
  const [hasSubmittedPR, setHasSubmittedPR] = useState(issue.status === 'completed')

  const isClaimedByCurrentUser = issue.claimed_by === currentUserId
  const isClaimedByOther = issue.claimed_by && issue.claimed_by !== currentUserId

  const handleClaim = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await claimIssue(issue.id, currentUserId, accessToken)
      
      if (result.success) {
        // Update local issue state
        setIssue({
          ...issue,
          status: 'claimed',
          claimed_by: currentUserId,
          claimed_at: result.claimed_at || new Date().toISOString(),
          claim_expires_at: result.claim_expires_at || null,
        })
        
        // Redirect to GitHub
        window.open(issue.github_url, '_blank')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to claim issue')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRelease = async () => {
    if (!confirm('Are you sure you want to release this issue? It will become available for others to claim.')) {
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      const result = await releaseIssue(issue.id, currentUserId, accessToken)
      
      if (result.success) {
        setIssue({
          ...issue,
          status: 'available',
          claimed_by: null,
          claimed_at: null,
          claim_expires_at: null,
        })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to release issue')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExtend = async () => {
    if (justification.length < 10) {
      setError('Please provide a justification (at least 10 characters)')
      return
    }

    setIsLoading(true)
    setError(null)
    
    try {
      const result = await extendClaimDeadline(
        issue.id,
        currentUserId,
        extensionDays,
        justification,
        accessToken
      )
      
      if (result.success) {
        setIssue({
          ...issue,
          claim_expires_at: result.new_expiration || issue.claim_expires_at,
        })
        setShowExtendModal(false)
        setJustification('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extend deadline')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoToGitHub = () => {
    window.open(issue.github_url, '_blank')
  }

  const handlePRSuccess = (result: SubmissionResult) => {
    // Update issue status
    setIssue({
      ...issue,
      status: 'completed',
    })
    
    // Hide form and show celebration
    setShowPRForm(false)
    setCelebrationResult(result)
    setHasSubmittedPR(true)
  }

  const handleCloseCelebration = () => {
    setCelebrationResult(null)
    // Refresh the page to show the PR management component
    router.refresh()
  }

  return (
    <div className="max-w-5xl mx-auto">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Repository Overview */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {issue.repository_full_name || issue.repository_name}
            </h1>
            {issue.programming_language && (
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                {issue.programming_language}
              </span>
            )}
          </div>
        </div>

        {repositorySummary ? (
          <div className="prose max-w-none">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">About this Repository</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{repositorySummary.summary}</p>
          </div>
        ) : (
          <div className="text-gray-500 italic">Loading repository information...</div>
        )}
      </div>

      {/* Issue Details */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">{issue.title}</h2>
          {issue.difficulty_level && (
            <span
              className={`px-3 py-1 text-sm font-medium rounded-full ${
                issue.difficulty_level === 'easy'
                  ? 'bg-green-100 text-green-800'
                  : issue.difficulty_level === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {issue.difficulty_level}
            </span>
          )}
        </div>

        {issue.labels.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {issue.labels.map((label) => (
              <span
                key={label}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
              >
                {label}
              </span>
            ))}
          </div>
        )}

        {issue.description && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
            <p className="text-gray-600 whitespace-pre-wrap">{issue.description}</p>
          </div>
        )}

        {issueExplanation ? (
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Explanation</h3>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap">{issueExplanation.explanation}</p>
            </div>

            {issueExplanation.learning_resources.length > 0 && (
              <div className="mt-4">
                <h4 className="text-md font-semibold text-gray-900 mb-2">Learning Resources</h4>
                <ul className="space-y-2">
                  {issueExplanation.learning_resources.map((resource, index) => (
                    <li key={index}>
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {resource.title}
                      </a>
                      {resource.description && (
                        <span className="text-gray-600 text-sm ml-2">- {resource.description}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="mt-6 text-gray-500 italic">Loading AI explanation...</div>
        )}
      </div>

      {/* Claim Status */}
      {issue.status === 'claimed' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-900">
                {isClaimedByCurrentUser ? 'You claimed this issue' : 'This issue is claimed'}
              </p>
              {issue.claim_expires_at && (
                <p className="text-sm text-blue-700 mt-1">
                  Time remaining:{' '}
                  <CountdownTimer expiresAt={issue.claim_expires_at} className="font-semibold" />
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-wrap gap-3">
          {issue.status === 'available' && (
            <button
              onClick={handleClaim}
              disabled={isLoading}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Claiming...' : 'Solve It'}
            </button>
          )}

          {isClaimedByCurrentUser && !hasSubmittedPR && (
            <>
              <button
                onClick={handleGoToGitHub}
                className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                Go to GitHub
              </button>

              <button
                onClick={() => setShowPRForm(!showPRForm)}
                className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
              >
                {showPRForm ? 'Cancel Submission' : 'Submit Pull Request'}
              </button>

              <button
                onClick={handleRelease}
                disabled={isLoading}
                className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Releasing...' : 'Release Issue'}
              </button>

              <button
                onClick={() => setShowExtendModal(true)}
                disabled={isLoading}
                className="px-6 py-3 bg-yellow-600 text-white font-medium rounded-lg hover:bg-yellow-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                Extend Deadline
              </button>
            </>
          )}

          {isClaimedByOther && (
            <button
              onClick={handleGoToGitHub}
              className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
            >
              View on GitHub
            </button>
          )}

          <button
            onClick={() => router.push('/issues')}
            className="px-6 py-3 bg-white text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
          >
            Back to Issues
          </button>
        </div>
      </div>

      {/* PR Submission Form */}
      {showPRForm && isClaimedByCurrentUser && !hasSubmittedPR && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Submit Your Pull Request
          </h3>
          <PRSubmissionForm
            issueId={issue.id}
            userId={currentUserId}
            accessToken={accessToken}
            onSuccess={handlePRSuccess}
            onCancel={() => setShowPRForm(false)}
          />
        </div>
      )}

      {/* PR Management - Show if PR has been submitted */}
      {hasSubmittedPR && (
        <PRManagement
          userId={currentUserId}
          issueId={issue.id}
          accessToken={accessToken}
        />
      )}

      {/* Extend Deadline Modal */}
      {showExtendModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Extend Deadline</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Extension Days (1-14)
              </label>
              <input
                type="number"
                min="1"
                max="14"
                value={extensionDays}
                onChange={(e) => setExtensionDays(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Justification (min 10 characters)
              </label>
              <textarea
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Explain why you need more time..."
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleExtend}
                disabled={isLoading || justification.length < 10}
                className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Extending...' : 'Extend'}
              </button>
              <button
                onClick={() => {
                  setShowExtendModal(false)
                  setJustification('')
                  setError(null)
                }}
                disabled={isLoading}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Celebration Modal */}
      {celebrationResult && (
        <ContributionCelebration
          result={celebrationResult}
          onClose={handleCloseCelebration}
        />
      )}
    </div>
  )
}
