"use client"

import { ComponentType } from "react"
import { ProtectedRoute } from "./ProtectedRoute"

export function withAuth<P extends object>(
  Component: ComponentType<P>,
  fallback?: React.ReactNode
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute fallback={fallback}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}
