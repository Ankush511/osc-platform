import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { fetchIssueById } from "@/lib/issues-api"
import { getCurrentUser } from "@/lib/users-api"
import IssueDetailClient from "@/components/issues/IssueDetailClient"
import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft } from "lucide-react"

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
        <div className="max-w-5xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/issues" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
              <ArrowLeft className="h-4 w-4" /> Back to Issues
            </Link>
            <Link href="/" className="flex items-center space-x-2">
              <LogoIcon size="sm" />
              <span className="text-sm font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Contributors.in</span>
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 lg:px-8 py-8">
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
