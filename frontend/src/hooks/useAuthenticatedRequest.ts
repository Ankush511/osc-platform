"use client"

import { useCallback } from "react"
import { useAuth } from "@/contexts/AuthContext"
import { api, APIError } from "@/lib/api-client"

export function useAuthenticatedRequest() {
  const { accessToken, signOut, refreshSession } = useAuth()

  const makeRequest = useCallback(
    async <T>(
      requestFn: (token: string) => Promise<T>,
      options: { retryOnAuthError?: boolean } = {}
    ): Promise<T> => {
      const { retryOnAuthError = true } = options

      if (!accessToken) {
        throw new Error("No access token available")
      }

      try {
        return await requestFn(accessToken)
      } catch (error) {
        if (error instanceof APIError) {
          // Handle authentication errors
          if (error.status === 401) {
            if (retryOnAuthError) {
              // Try to refresh the session
              try {
                await refreshSession()
                // Retry the request with new token
                if (accessToken) {
                  return await requestFn(accessToken)
                }
              } catch (refreshError) {
                // Refresh failed, sign out
                await signOut()
                throw new Error("Session expired. Please sign in again.")
              }
            } else {
              await signOut()
              throw new Error("Session expired. Please sign in again.")
            }
          }

          // Handle other API errors
          throw error
        }

        // Handle non-API errors
        throw error
      }
    },
    [accessToken, signOut, refreshSession]
  )

  const get = useCallback(
    <T>(endpoint: string) => makeRequest<T>((token) => api.get<T>(endpoint, token)),
    [makeRequest]
  )

  const post = useCallback(
    <T>(endpoint: string, data?: any) =>
      makeRequest<T>((token) => api.post<T>(endpoint, data, token)),
    [makeRequest]
  )

  const put = useCallback(
    <T>(endpoint: string, data?: any) =>
      makeRequest<T>((token) => api.put<T>(endpoint, data, token)),
    [makeRequest]
  )

  const patch = useCallback(
    <T>(endpoint: string, data?: any) =>
      makeRequest<T>((token) => api.patch<T>(endpoint, data, token)),
    [makeRequest]
  )

  const del = useCallback(
    <T>(endpoint: string) => makeRequest<T>((token) => api.delete<T>(endpoint, token)),
    [makeRequest]
  )

  return {
    get,
    post,
    put,
    patch,
    delete: del,
  }
}
