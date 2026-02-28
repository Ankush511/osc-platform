import { auth } from "@/auth"
import { redirect } from "next/navigation"
import IssueDiscoveryClient from "@/components/issues/IssueDiscoveryClient"
import { fetchAvailableFilters } from "@/lib/issues-api"

export default async function IssuesPage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  // Fetch available filters for the filter sidebar
  let availableFilters = null
  try {
    availableFilters = await fetchAvailableFilters(session.accessToken)
  } catch (error) {
    console.error('Error fetching available filters:', error)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                Discover Issues
              </h1>
            </div>
            <div className="flex items-center gap-4">
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
        <IssueDiscoveryClient 
          accessToken={session.accessToken}
          availableFilters={availableFilters}
        />
      </main>
    </div>
  )
}
