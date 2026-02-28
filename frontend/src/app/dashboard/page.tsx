import { auth, signOut } from "@/auth"
import { redirect } from "next/navigation"
import StatsCard from "@/components/dashboard/StatsCard"
import AchievementBadge from "@/components/dashboard/AchievementBadge"
import ContributionTimeline from "@/components/dashboard/ContributionTimeline"
import LanguageBreakdown from "@/components/dashboard/LanguageBreakdown"
import RepositoryBreakdown from "@/components/dashboard/RepositoryBreakdown"
import { DashboardData } from "@/types/dashboard"

async function getDashboardData(accessToken: string): Promise<DashboardData | null> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me/dashboard`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      cache: 'no-store',
    })

    if (!response.ok) {
      console.error('Failed to fetch dashboard data:', response.statusText)
      return null
    }

    return response.json()
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
    return null
  }
}

export default async function DashboardPage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const dashboardData = await getDashboardData(session.accessToken)

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to load dashboard</h2>
          <p className="text-gray-600">Please try refreshing the page</p>
        </div>
      </div>
    )
  }

  const { user, statistics, achievements, achievement_stats } = dashboardData
  const unlockedAchievements = achievements.filter(a => a.is_unlocked)
  const inProgressAchievements = achievements.filter(a => !a.is_unlocked && a.progress > 0)
  const lockedAchievements = achievements.filter(a => !a.is_unlocked && a.progress === 0)

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Open Source Contribution Platform
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="/issues"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Discover Issues
              </a>
              <a
                href="/profile"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Profile
              </a>
              <a
                href="/settings"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Settings
              </a>
              <div className="flex items-center gap-3">
                <img
                  src={user.avatar_url}
                  alt={user.github_username}
                  className="h-8 w-8 rounded-full"
                />
                <span className="text-sm font-medium text-gray-700">
                  {user.full_name || user.github_username}
                </span>
              </div>
              <form
                action={async () => {
                  "use server"
                  await signOut({ redirectTo: "/" })
                }}
              >
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Sign Out
                </button>
              </form>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Welcome back, {user.full_name || user.github_username}! 👋
            </h2>
            <p className="mt-2 text-gray-600">
              Track your open source journey and celebrate your achievements
            </p>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Total Contributions"
              value={statistics.total_contributions}
              icon="📊"
              description="All time"
            />
            <StatsCard
              title="PRs Submitted"
              value={statistics.total_prs_submitted}
              icon="📝"
              description="Pending and merged"
            />
            <StatsCard
              title="PRs Merged"
              value={statistics.merged_prs}
              icon="✅"
              description="Successfully merged"
            />
            <StatsCard
              title="Achievements"
              value={`${achievement_stats.unlocked_achievements}/${achievement_stats.total_achievements}`}
              icon="🏆"
              description={`${achievement_stats.completion_percentage.toFixed(0)}% complete`}
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Timeline and Breakdowns */}
            <div className="lg:col-span-2 space-y-6">
              {/* Contribution Timeline */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent Contributions
                </h3>
                <ContributionTimeline contributions={statistics.recent_contributions} />
              </div>

              {/* Language Breakdown */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Contributions by Language
                </h3>
                <LanguageBreakdown contributions={statistics.contributions_by_language} />
              </div>

              {/* Repository Breakdown */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Top Repositories
                </h3>
                <RepositoryBreakdown contributions={statistics.contributions_by_repo} />
              </div>
            </div>

            {/* Right Column - Achievements */}
            <div className="space-y-6">
              {/* Unlocked Achievements */}
              {unlockedAchievements.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Unlocked Achievements 🎉
                  </h3>
                  <div className="space-y-4">
                    {unlockedAchievements.map((achievement) => (
                      <AchievementBadge
                        key={achievement.achievement.id}
                        achievement={achievement}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* In Progress Achievements */}
              {inProgressAchievements.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    In Progress
                  </h3>
                  <div className="space-y-4">
                    {inProgressAchievements.slice(0, 5).map((achievement) => (
                      <AchievementBadge
                        key={achievement.achievement.id}
                        achievement={achievement}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Locked Achievements */}
              {lockedAchievements.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Locked Achievements
                  </h3>
                  <div className="space-y-4">
                    {lockedAchievements.slice(0, 3).map((achievement) => (
                      <AchievementBadge
                        key={achievement.achievement.id}
                        achievement={achievement}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
