import { auth } from "@/auth"
import { redirect } from "next/navigation"
import { getCurrentUser } from "@/lib/users-api"
import PreferencesForm from "@/components/settings/PreferencesForm"
import Link from "next/link"

export default async function SettingsPage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  const user = await getCurrentUser(session.accessToken)

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
              <Link
                href="/profile"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Profile
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="mt-2 text-gray-600">
            Manage your preferences and customize your experience
          </p>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-5 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Preferences</h2>
            <p className="mt-1 text-sm text-gray-600">
              Set your preferred programming languages and issue labels to personalize your issue discovery experience
            </p>
          </div>

          <div className="px-6 py-6">
            <PreferencesForm
              initialLanguages={user.preferred_languages}
              initialLabels={user.preferred_labels}
            />
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">About Preferences</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  Your preferences will be used to filter and prioritize issues in the discovery page. 
                  You can always change these settings later.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
