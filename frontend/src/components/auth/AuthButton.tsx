"use client"

import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"

export function AuthButton() {
  const { user, isAuthenticated, isLoading, signOut } = useAuth()
  const router = useRouter()

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse"></div>
        <div className="h-4 w-24 bg-gray-200 rounded animate-pulse"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <button
        onClick={() => router.push("/auth/signin")}
        className="px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-md hover:bg-gray-800 transition-colors"
      >
        Sign In
      </button>
    )
  }

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-3">
        {user?.image && (
          <img
            src={user.image}
            alt={user.name || "User"}
            className="h-8 w-8 rounded-full"
          />
        )}
        <span className="text-sm font-medium text-gray-700">
          {user?.name || user?.email}
        </span>
      </div>
      <button
        onClick={() => signOut()}
        className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
      >
        Sign Out
      </button>
    </div>
  )
}
