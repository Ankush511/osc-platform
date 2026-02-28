'use client'

import { useEffect, useState } from 'react'
import { SubmissionResult } from '@/types/contribution'

interface ContributionCelebrationProps {
  result: SubmissionResult
  onClose: () => void
}

export default function ContributionCelebration({
  result,
  onClose,
}: ContributionCelebrationProps) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Trigger animation after mount
    setTimeout(() => setIsVisible(true), 100)
  }, [])

  const isMerged = result.status === 'merged'

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div
        className={`bg-white rounded-lg p-8 max-w-md w-full transform transition-all duration-500 ${
          isVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
      >
        {/* Celebration Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            {/* Animated circles */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 bg-green-100 rounded-full animate-ping opacity-75"></div>
            </div>
            
            {/* Main icon */}
            <div className="relative bg-green-500 rounded-full p-6">
              <svg
                className="w-12 h-12 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Success Message */}
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {isMerged ? '🎉 Contribution Merged!' : '✨ PR Submitted!'}
          </h2>
          <p className="text-gray-600">
            {isMerged
              ? 'Your pull request has been merged! Congratulations on your contribution!'
              : 'Your pull request has been submitted successfully and is now under review.'}
          </p>
        </div>

        {/* Stats */}
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                #{result.pr_number}
              </div>
              <div className="text-xs text-gray-600 mt-1">Pull Request</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                +{result.points_earned}
              </div>
              <div className="text-xs text-gray-600 mt-1">Points Earned</div>
            </div>
          </div>
        </div>

        {/* Encouragement */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-yellow-800 text-center">
            {isMerged
              ? '🌟 Keep up the great work! Your contribution makes a difference.'
              : '⏳ Hang tight! Maintainers will review your PR soon.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <a
            href={`https://github.com/pulls`}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full px-6 py-3 bg-gray-900 text-white text-center font-medium rounded-lg hover:bg-gray-800 transition-colors"
          >
            View on GitHub
          </a>
          
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Continue
          </button>
        </div>

        {/* Confetti effect for merged PRs */}
        {isMerged && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-r from-yellow-400 to-pink-500 rounded-full animate-bounce"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: `-${Math.random() * 20}%`,
                  animationDelay: `${Math.random() * 2}s`,
                  animationDuration: `${2 + Math.random() * 2}s`,
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
