import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import AchievementBadge from '../AchievementBadge'
import { UserAchievementProgress } from '@/types/dashboard'

describe('AchievementBadge', () => {
  const mockUnlockedAchievement: UserAchievementProgress = {
    achievement: {
      id: 1,
      name: 'First Contribution',
      description: 'Submit your first pull request',
      badge_icon: '🎉',
      category: 'milestone',
      threshold: 1,
      created_at: '2024-01-01T00:00:00Z',
    },
    progress: 1,
    is_unlocked: true,
    earned_at: '2024-01-15T00:00:00Z',
    percentage: 100,
  }

  const mockLockedAchievement: UserAchievementProgress = {
    achievement: {
      id: 2,
      name: 'Contributor',
      description: 'Submit 10 pull requests',
      badge_icon: '🏆',
      category: 'milestone',
      threshold: 10,
      created_at: '2024-01-01T00:00:00Z',
    },
    progress: 3,
    is_unlocked: false,
    earned_at: null,
    percentage: 30,
  }

  it('renders unlocked achievement correctly', () => {
    render(<AchievementBadge achievement={mockUnlockedAchievement} />)
    
    expect(screen.getByText('First Contribution')).toBeInTheDocument()
    expect(screen.getByText('Submit your first pull request')).toBeInTheDocument()
    expect(screen.getByText('🎉')).toBeInTheDocument()
    expect(screen.getByText('Unlocked')).toBeInTheDocument()
    expect(screen.getByText('1 / 1')).toBeInTheDocument()
  })

  it('renders locked achievement correctly', () => {
    render(<AchievementBadge achievement={mockLockedAchievement} />)
    
    expect(screen.getByText('Contributor')).toBeInTheDocument()
    expect(screen.getByText('Submit 10 pull requests')).toBeInTheDocument()
    expect(screen.getByText('🏆')).toBeInTheDocument()
    expect(screen.queryByText('Unlocked')).not.toBeInTheDocument()
    expect(screen.getByText('3 / 10')).toBeInTheDocument()
  })

  it('displays progress bar with correct width', () => {
    const { container } = render(<AchievementBadge achievement={mockLockedAchievement} />)
    
    const progressBar = container.querySelector('.h-2.rounded-full:not(.bg-gray-200)')
    expect(progressBar).toHaveAttribute('style', expect.stringContaining('width'))
  })

  it('applies correct styling for unlocked achievement', () => {
    const { container } = render(<AchievementBadge achievement={mockUnlockedAchievement} />)
    
    const badge = container.querySelector('.border-green-500')
    expect(badge).toBeInTheDocument()
  })

  it('applies correct styling for locked achievement', () => {
    const { container } = render(<AchievementBadge achievement={mockLockedAchievement} />)
    
    const badge = container.querySelector('.border-gray-300')
    expect(badge).toBeInTheDocument()
  })
})
