import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/users-api"
import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import {
  ArrowLeft,
  Github,
  MapPin,
  Mail,
  Calendar,
  GitPullRequest,
  GitMerge,
  Settings,
  ExternalLink,
  CheckCircle2,
  User,
} from "lucide-react"

export default async function ProfilePage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const user = await getCurrentUser(session.accessToken)

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })

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
            <div className="flex items-center gap-3">
              <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
                <ArrowLeft className="h-4 w-4" /> Dashboard
              </Link>
              <Link href="/settings" className="text-gray-400 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/5">
                <Settings className="h-5 w-5" />
              </Link>
              <Link href="/dashboard" className="flex items-center gap-2 pl-3 border-l border-white/10">
                {session.user?.image ? (
                  <img src={session.user.image} alt="" className="h-8 w-8 rounded-full ring-2 ring-cyan-500/30" />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-8">
        {/* Profile Header Card */}
        <div className="relative mb-8">
          {/* Banner */}
          <div className="h-36 rounded-t-3xl bg-gradient-to-r from-cyan-500/30 via-blue-500/30 to-purple-500/30 border border-white/10 border-b-0" />

          {/* Profile info */}
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 border-t-0 rounded-b-3xl px-6 pb-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-end -mt-14 gap-5">
              <img
                src={user.avatar_url}
                alt={user.github_username}
                className="h-28 w-28 rounded-2xl border-4 border-black shadow-2xl shadow-cyan-500/20 ring-2 ring-cyan-500/30"
              />
              <div className="flex-1 pb-1">
                <h1 className="text-2xl sm:text-3xl font-black text-white">
                  {user.full_name || user.github_username}
                </h1>
                <p className="text-gray-400 text-sm mt-0.5">@{user.github_username}</p>
              </div>
              <a
                href={`https://github.com/${user.github_username}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 hover:text-white hover:border-cyan-500/30 transition-all"
              >
                <Github className="h-4 w-4" />
                GitHub Profile
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </div>

            {/* Bio */}
            {user.bio && (
              <p className="text-gray-400 text-sm mt-5 max-w-2xl leading-relaxed">{user.bio}</p>
            )}

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-4 mt-4 text-xs text-gray-500">
              {user.location && (
                <span className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5" />
                  {user.location}
                </span>
              )}
              {user.email && (
                <span className="flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5" />
                  {user.email}
                </span>
              )}
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5" />
                Joined {formatDate(user.created_at)}
              </span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 group hover:border-cyan-500/30 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-cyan-500/15">
                <GitPullRequest className="h-5 w-5 text-cyan-400" />
              </div>
              <span className="text-sm font-medium text-gray-400">Total Contributions</span>
            </div>
            <div className="text-4xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              {user.total_contributions}
            </div>
          </div>
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 group hover:border-emerald-500/30 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-500/15">
                <GitMerge className="h-5 w-5 text-emerald-400" />
              </div>
              <span className="text-sm font-medium text-gray-400">Merged PRs</span>
            </div>
            <div className="text-4xl font-black bg-gradient-to-r from-emerald-400 to-green-500 bg-clip-text text-transparent">
              {user.merged_prs}
            </div>
          </div>
        </div>

        {/* GitHub Integration */}
        <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-emerald-500/15">
              <CheckCircle2 className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">GitHub Connected</p>
              <p className="text-xs text-gray-500">Your account is linked to GitHub · ID {user.github_id}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
