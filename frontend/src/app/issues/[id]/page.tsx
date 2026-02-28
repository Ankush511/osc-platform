import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { fetchIssueById } from "@/lib/issues-api"
import { fetchRepositorySummary, fetchIssueExplanation } from "@/lib/ai-api"
import IssueDetailClient from "@/components/issues/IssueDetailClient"

interface IssueDetailPageProps {
  params: {
    id: string
  }
}

export default async function IssueDetailPage({ params }: IssueDetailPageProps) {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const issueId = parseInt(params.id)

  if (isNaN(issueId)) {
    redirect("/issues")
  }

  // Fetch issue data
  let issue
  try {
    issue = await fetchIssueById(issueId, session.accessToken)
  } catch (error) {
    console.error('Error fetching issue:', error)
    redirect("/issues")
  }

  // Fetch AI-generated content in parallel
  const [repositorySummary, issueExplanation] = await Promise.allSettled([
    fetchRepositorySummary(issue.repository_id, session.accessToken),
    fetchIssueExplanation(issueId, session.accessToken),
  ])

  const repoSummary = repositorySummary.status === 'fulfilled' ? repositorySummary.value : null
  const issueExp = issueExplanation.status === 'fulfilled' ? issueExplanation.value : null

  // Get current user ID from session
  const currentUserId = session.user.id ? parseInt(session.user.id) : 0

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Issue Details
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <a
                href="/issues"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Browse Issues
              </a>
              <a
                href="/dashboard"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Dashboard
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <IssueDetailClient
          issue={issue}
          repositorySummary={repoSummary}
          issueExplanation={issueExp}
          accessToken={session.accessToken}
          currentUserId={currentUserId}
        />
      </main>
    </div>
  )
}
