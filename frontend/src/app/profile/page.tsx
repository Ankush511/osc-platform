import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/users-api"
import Link from "next/link"

export default async function ProfilePage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const user = await getCurrentUser(session.accessToken)

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                Open Source Contribution Platform
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/issues"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Discover Issues
              </Link>
              <Link
                href="/dashboard"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-32"></div>
          
          <div className="px-6 pb-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-end -mt-16 mb-6">
              <img
                src={user.avatar_url}
                alt={user.github_username}
                className="h-32 w-32 rounded-full border-4 border-white shadow-lg"
              />
              <div className="mt-4 sm:mt-0 sm:ml-6 flex-1">
                <h1 className="text-3xl font-bold text-gray-900">
                  {user.full_name || user.github_username}
                </h1>
                <p className="text-gray-600 mt-1">@{user.github_username}</p>
                <div className="flex gap-4 mt-3">
                  <a
                    href={`https://github.com/${user.github_username}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                  >
                    View GitHub Profile
                  </a>
                  <Link
                    href="/settings"
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Edit Preferences
                  </Link>
                </div>
              </div>
            </div>

            {/* Profile Information */}
            <div className="border-t border-gray-200 pt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h2>
              
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                {user.bio && (
                  <div className="sm:col-span-2">
                    <dt className="text-sm font-medium text-gray-500">Bio</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user.bio}</dd>
                  </div>
                )}
                
                {user.location && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Location</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user.location}</dd>
                  </div>
                )}
                
                {user.email && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="mt-1 text-sm text-gray-900">{user.email}</dd>
                  </div>
                )}
                
                <div>
                  <dt className="text-sm font-medium text-gray-500">GitHub ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">{user.github_id}</dd>
                </div>
                
                <div>
                  <dt className="text-sm font-medium text-gray-500">Member Since</dt>
                  <dd className="mt-1 text-sm text-gray-900">{formatDate(user.created_at)}</dd>
                </div>
              </dl>
            </div>

            {/* Contribution Stats */}
            <div className="border-t border-gray-200 pt-6 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Contribution Statistics</h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-3xl font-bold text-blue-600">{user.total_contributions}</div>
                  <div className="text-sm text-gray-600 mt-1">Total Contributions</div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-3xl font-bold text-green-600">{user.merged_prs}</div>
                  <div className="text-sm text-gray-600 mt-1">Merged Pull Requests</div>
                </div>
              </div>
            </div>

            {/* Preferences */}
            <div className="border-t border-gray-200 pt-6 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferences</h2>
              
              <div className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500 mb-2">Preferred Languages</dt>
                  <dd className="flex flex-wrap gap-2">
                    {user.preferred_languages.length > 0 ? (
                      user.preferred_languages.map((lang) => (
                        <span
                          key={lang}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                        >
                          {lang}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No preferred languages set</span>
                    )}
                  </dd>
                </div>
                
                <div>
                  <dt className="text-sm font-medium text-gray-500 mb-2">Preferred Labels</dt>
                  <dd className="flex flex-wrap gap-2">
                    {user.preferred_labels.length > 0 ? (
                      user.preferred_labels.map((label) => (
                        <span
                          key={label}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                        >
                          {label}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No preferred labels set</span>
                    )}
                  </dd>
                </div>
              </div>
            </div>

            {/* GitHub Integration Status */}
            <div className="border-t border-gray-200 pt-6 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">GitHub Integration</h2>
              
              <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-green-800">Connected to GitHub</p>
                  <p className="text-sm text-green-700">Your GitHub account is successfully linked</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
