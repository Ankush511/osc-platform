import { auth } from "@/auth"
import { redirect } from "next/navigation"

/**
 * Server-side utility to require authentication
 * Redirects to sign-in page if not authenticated
 */
export async function requireAuth() {
  const session = await auth()
  
  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }
  
  return session
}

/**
 * Server-side utility to get optional authentication
 * Returns null if not authenticated
 */
export async function getAuth() {
  const session = await auth()
  
  if (!session?.user || !session.accessToken) {
    return null
  }
  
  return session
}

/**
 * Check if user has a valid session with access token
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await auth()
  return !!(session?.user && session.accessToken)
}
