"use client"

import { createContext, useContext, ReactNode, useCallback, useEffect, useState } from "react"
import { useSession, signOut as nextAuthSignOut } from "next-auth/react"
import { useRouter } from "next/navigation"

interface User {
  id?: string
  name?: string | null
  email?: string | null
  image?: string | null
}

interface AuthContextType {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  signOut: () => Promise<void>
  refreshSession: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, status, update } = useSession()
  const router = useRouter()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const user = session?.user || null
  const accessToken = session?.accessToken || null
  const isAuthenticated = status === "authenticated"
  const isLoading = status === "loading" || isRefreshing

  const signOut = useCallback(async () => {
    try {
      await nextAuthSignOut({ callbackUrl: "/" })
    } catch (error) {
      console.error("Sign out error:", error)
      router.push("/auth/error?error=SignOutFailed")
    }
  }, [router])

  const refreshSession = useCallback(async () => {
    try {
      setIsRefreshing(true)
      await update()
    } catch (error) {
      console.error("Session refresh error:", error)
      // If refresh fails, sign out the user
      await signOut()
    } finally {
      setIsRefreshing(false)
    }
  }, [update, signOut])

  // Auto-refresh session periodically
  useEffect(() => {
    if (!isAuthenticated) return

    const interval = setInterval(() => {
      refreshSession()
    }, 5 * 60 * 1000) // Refresh every 5 minutes

    return () => clearInterval(interval)
  }, [isAuthenticated, refreshSession])

  const value: AuthContextType = {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    signOut,
    refreshSession,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
