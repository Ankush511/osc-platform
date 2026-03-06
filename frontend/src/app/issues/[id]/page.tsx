import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { fetchIssueById } from "@/lib/issues-api"
import { getCurrentUser } from "@/lib/users-api"
import IssueDetailClient from "@/components/issues/IssueDetailClient"
import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, User } from "lucide-react"

export const dynamic = 'force-dynamic'

interface Props {
  params: Promise<{ id: string }>
}

export default async function IssueDetailPage({ params }: Props) {
  const { id } = await params
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const issueId = parseInt(id)
  if (isNaN(issueId)) redirect("/issues")

  let issue
  let currentUserId = 0
  try {
    const [issueData, userData] = await Promise.all([
      fetchIssueById(issueId, session.accessToken),
      getCurrentUser(session.accessToken),
    ])
    issue = issueData
    currentUserId = userData.id
  } catch {
    redirect("/issues")
  }

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
              <Link href="/issues" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
                <ArrowLeft className="h-4 w-4" /> Back to Issues
              </Link>
              <Link href="/dashboard" className="flex items-center gap-2 pl-3 border-l border-white/10">
                {session.user?.image ? (
                  <img src={session.user.image} alt="" className="h-8 w-8 rounded-full ring-2 ring-cyan-500/30" />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
                <span className="hidden sm:block text-sm font-medium text-gray-300">{session.user?.name}</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-8">
        <IssueDetailClient
          key={issue.id}
          issue={issue}
          accessToken={session.accessToken}
          currentUserId={currentUserId}
        />
      </main>
    </div>
  )
}
