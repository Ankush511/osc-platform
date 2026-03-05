import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { Award, ArrowLeft, Info } from "lucide-react"

export const metadata = { title: "Achievements — Contributors.in" }

const MILESTONE_ACHIEVEMENTS = [
  { icon: "🎯", name: "First Steps", description: "Submit your first pull request", threshold: "1 PR submitted", category: "Getting Started" },
  { icon: "✅", name: "Getting Started", description: "Get your first PR merged", threshold: "1 PR merged", category: "Getting Started" },
  { icon: "🌟", name: "Contributor", description: "Submit 5 pull requests", threshold: "5 PRs submitted", category: "Consistency" },
  { icon: "⭐", name: "Active Contributor", description: "Get 5 PRs merged", threshold: "5 PRs merged", category: "Consistency" },
  { icon: "💪", name: "Dedicated Developer", description: "Submit 10 pull requests", threshold: "10 PRs submitted", category: "Dedication" },
  { icon: "🏆", name: "Merge Master", description: "Get 10 PRs merged", threshold: "10 PRs merged", category: "Dedication" },
  { icon: "🦸", name: "Open Source Hero", description: "Submit 25 pull requests", threshold: "25 PRs submitted", category: "Mastery" },
  { icon: "💯", name: "Century Club", description: "Get 25 PRs merged", threshold: "25 PRs merged", category: "Mastery" },
]

const LANGUAGE_ACHIEVEMENTS = [
  { icon: "🐍", name: "Python Pioneer", description: "Contribute to 5 Python projects", threshold: "5 Python contributions" },
  { icon: "📜", name: "JavaScript Journeyman", description: "Contribute to 5 JavaScript projects", threshold: "5 JavaScript contributions" },
  { icon: "📘", name: "TypeScript Titan", description: "Contribute to 5 TypeScript projects", threshold: "5 TypeScript contributions" },
  { icon: "🔵", name: "Go Guru", description: "Contribute to 5 Go projects", threshold: "5 Go contributions" },
  { icon: "🦀", name: "Rust Ranger", description: "Contribute to 5 Rust projects", threshold: "5 Rust contributions" },
  { icon: "🌐", name: "Polyglot", description: "Contribute to projects in 3 different languages", threshold: "3 different languages" },
]

export default function AchievementsPage() {
  return (
    <div className="min-h-screen bg-black relative">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

      <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
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
            <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
              <ArrowLeft className="h-4 w-4" /> Home
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-purple-500/20 to-cyan-500/20 mb-6">
            <Award className="h-10 w-10 text-purple-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">Achievements</h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Earn badges as you contribute to open source. Each achievement represents a milestone in your developer journey.
          </p>
        </div>

        {/* Milestone Achievements */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-2">Milestone Achievements</h2>
          <p className="text-gray-500 text-sm mb-8">Earned by reaching contribution milestones</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {MILESTONE_ACHIEVEMENTS.map((a) => (
              <div key={a.name} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-cyan-500/20 transition-all">
                <div className="text-4xl mb-4">{a.icon}</div>
                <h3 className="text-base font-bold text-white mb-1">{a.name}</h3>
                <p className="text-gray-400 text-sm mb-3 leading-relaxed">{a.description}</p>
                <span className="inline-block px-2.5 py-1 rounded-lg text-[11px] font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {a.threshold}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Language Achievements */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold text-white mb-2">Language Achievements</h2>
          <p className="text-gray-500 text-sm mb-8">Earned by contributing across different programming languages</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {LANGUAGE_ACHIEVEMENTS.map((a) => (
              <div key={a.name} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-purple-500/20 transition-all">
                <div className="text-4xl mb-4">{a.icon}</div>
                <h3 className="text-base font-bold text-white mb-1">{a.name}</h3>
                <p className="text-gray-400 text-sm mb-3 leading-relaxed">{a.description}</p>
                <span className="inline-block px-2.5 py-1 rounded-lg text-[11px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  {a.threshold}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Note */}
        <div className="bg-gradient-to-br from-cyan-500/[0.06] to-blue-500/[0.03] backdrop-blur-sm border border-cyan-500/15 rounded-2xl p-6 flex items-start gap-4">
          <Info className="h-5 w-5 text-cyan-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-sm text-gray-300 leading-relaxed">
              New achievements are added every month based on community feedback and platform growth. Keep contributing and check back regularly to discover new badges to earn.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
