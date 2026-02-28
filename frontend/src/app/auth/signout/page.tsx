"use client"

import { signOut } from "next-auth/react"
import { useEffect } from "react"

export default function SignOutPage() {
  useEffect(() => {
    signOut({ callbackUrl: "/" })
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            Signing out...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we sign you out
          </p>
        </div>
      </div>
    </div>
  )
}
