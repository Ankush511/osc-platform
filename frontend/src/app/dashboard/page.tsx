import { auth, signOut } from "@/auth"
import { redirect } from "next/navigation"

export const dynamic = 'force-dynamic'
import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, LogOut, Settings, User, Target, Sparkles, GitPullRequest, Trophy, BarChart3 } from "lucide-react"
import StatsCard from "@/components/dashboard/StatsCard"
import AchievementBadge from "@/components/dashboard/AchievementBadge"
import ContributionTimeline from "@/components/dashboard/ContributionTimeline"
import LanguageBreakdown from "@/components/dashboard/LanguageBreakdown"
import RepositoryBreakdown from "@/components/dashboard/RepositoryBreakdown"
import { DashboardData } from "@/types/dashboard"

async function getDashboardData(accessToken: string): Promise<DashboardData | null> {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me/dashboard`,
      {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      }
    )
    if (!response.ok) return null
    return response.json()
  } catch {
    return null
  }
}

export default async function DashboardPage() {
  const session = await auth()

  if (!session?.user) {
    redirect("/auth/signin")
  }

  if (!session.accessToken) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <div className="text-center max-w-md bg-gradient-to-br from-white/[0.07] to-white/[0.02] border border-white/10 rounded-2xl p-8">
          <Sparkles className="h-10 w-10 text-cyan-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Session sync issue</h2>
          <p className="text-gray-400 text-sm mb-6">
            GitHub login succeeded but we couldn&apos;t connect to the backend. Sign out and try again.
          </p>
          <form action={async () => { "use server"; await signOut({ redirectTo: "/auth/signin" }) }}>
            <button type="submit" className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all">
              Sign out &amp; retry
            </button>
          </form>
        </div>
      </div>
    )
  }

  const dashboardData = await getDashboardData(session.accessToken)

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center px-4">
        <div className="text-center bg-gradient-to-br from-white/[0.07] to-white/[0.02] border border-white/10 rounded-2xl p-8">
          <h2 className="text-xl font-bold text-white mb-2">Unable to load dashboard</h2>
          <p className="text-gray-400 text-sm">Please try refreshing the page.</p>
        </div>
      </div>
    )
  }

  const { user, statistics, achievements, achievement_stats } = dashboardData
  const unlockedAchievements = achievements.filter((a) => a.is_unlocked)
  const inProgressAchievements = achievements.filter((a) => !a.is_unlocked && a.progress > 0)
  const lockedAchievements = achievements.filter((a) => !a.is_unlocked && a.progress === 0)

  return (
    <div className="min-h-screen bg-black relative">
      {/* Background grid */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                <LogoIcon size="md" />
              </div>
              <div>
                <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Contributors</span>
                <span className="text-cyan-400 text-xs font-mono">.in</span>
              </div>
            </Link>

            <div className="flex items-center gap-3">
              <Link href="/issues" className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold hover:from-cyan-400 hover:to-blue-500 transition-all">
                <Target className="h-4 w-4" />
                Discover Issues
              </Link>
              <Link href="/profile" className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5">
                <User className="h-5 w-5" />
              </Link>
              <Link href="/settings" className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5">
                <Settings className="h-5 w-5" />
              </Link>
              <div className="flex items-center gap-2 pl-3 border-l border-white/10">
                <img src={user.avatar_url} alt={user.github_username} className="h-8 w-8 rounded-full ring-2 ring-cyan-500/30" />
                <span className="hidden sm:block text-sm font-medium text-gray-300">{user.full_name || user.github_username}</span>
              </div>
              <form action={async () => { "use server"; await signOut({ redirectTo: "/" }) }}>
                <button type="submit" className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5">
                  <LogOut className="h-5 w-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-black text-white mb-2">
            Welcome back, <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">{user.full_name || user.github_username}</span> 👋
          </h1>
          <p className="text-gray-400">Track your open source journey and celebrate your achievements</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatsCard title="Total Contributions" value={statistics.total_contributions} iconName="BarChart3" description="All time" index={0} />
          <StatsCard title="PRs Submitted" value={statistics.total_prs_submitted} iconName="GitPullRequest" description="Pending and merged" index={1} />
          <StatsCard title="PRs Merged" value={statistics.merged_prs} iconName="GitMerge" description="Successfully merged" index={2} />
          <StatsCard title="Achievements" value={`${achievement_stats.unlocked_achievements}/${achievement_stats.total_achievements}`} iconName="Trophy" description="Unlocked" index={3} />
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Timeline */}
            <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <GitPullRequest className="h-5 w-5 text-cyan-400" />
                Recent Contributions
              </h3>
              <ContributionTimeline contributions={statistics.recent_contributions} />
            </div>

            {/* Language Breakdown */}
            <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <GitPullRequest className="h-5 w-5 text-cyan-400" />
                Languages
              </h3>
              <LanguageBreakdown contributions={statistics.contributions_by_language} />
            </div>

            {/* Repository Breakdown */}
            <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-cyan-400" />
                Top Repositories
              </h3>
              <RepositoryBreakdown contributions={statistics.contributions_by_repo} />
            </div>
          </div>

          {/* Right Column — Achievements */}
          <div className="space-y-6">
            {unlockedAchievements.length > 0 && (
              <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-cyan-400" />
                  Unlocked 🎉
                </h3>
                <div className="space-y-3">
                  {unlockedAchievements.map((a, i) => (
                    <AchievementBadge key={a.achievement.id} achievement={a} index={i} />
                  ))}
                </div>
              </div>
            )}

            {inProgressAchievements.length > 0 && (
              <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-cyan-400" />
                  In Progress
                </h3>
                <div className="space-y-3">
                  {inProgressAchievements.slice(0, 5).map((a, i) => (
                    <AchievementBadge key={a.achievement.id} achievement={a} index={i} />
                  ))}
                </div>
              </div>
            )}

            {lockedAchievements.length > 0 && (
              <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Target className="h-5 w-5 text-gray-500" />
                  Locked
                </h3>
                <div className="space-y-3">
                  {lockedAchievements.slice(0, 3).map((a, i) => (
                    <AchievementBadge key={a.achievement.id} achievement={a} index={i} />
                  ))}
                </div>
              </div>
            )}

            {achievements.length === 0 && (
              <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center">
                <Trophy className="h-10 w-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 text-sm">Start contributing to unlock achievements</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
