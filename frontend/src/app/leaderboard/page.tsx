import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { Trophy, Clock, ArrowLeft } from "lucide-react"

export const metadata = { title: "Leaderboard — Contributors.in" }

export default function LeaderboardPage() {
  return (
    <div className="min-h-screen bg-black relative">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

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
            <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
              <ArrowLeft className="h-4 w-4" /> Home
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 lg:px-8 py-24">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br from-amber-500/20 to-yellow-500/20 mb-8">
            <Trophy className="h-12 w-12 text-amber-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">Leaderboard</h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto mb-12">
            See who&apos;s leading the open source contribution race. Compete with developers worldwide and climb the ranks.
          </p>

          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-3xl p-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 mb-6">
              <Clock className="h-8 w-8 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">Stay Tuned</h2>
            <p className="text-gray-400 text-base max-w-md mx-auto leading-relaxed mb-6">
              We&apos;re building something exciting. The leaderboard will be live soon with weekly, monthly, and all-time rankings across languages and repositories.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {["Weekly Rankings", "Monthly Rankings", "All-Time Rankings", "Language-Specific", "Repository-Specific"].map((tag) => (
                <span key={tag} className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/5 text-gray-400 border border-white/10">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
