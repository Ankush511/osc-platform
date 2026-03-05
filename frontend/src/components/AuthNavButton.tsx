"use client"

import { useSession } from "next-auth/react"
import Link from "next/link"
import { Github, ArrowRight, LayoutDashboard } from "lucide-react"

export function AuthNavButton() {
  const { status } = useSession()

  if (status === "loading") {
    return <div className="w-[120px] h-[40px] rounded-xl bg-white/5 animate-pulse" />
  }

  if (status === "authenticated") {
    return (
      <Link
        href="/dashboard"
        className="group inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm transition-all duration-300"
      >
        <LayoutDashboard className="h-4 w-4" />
        <span>Dashboard</span>
        <ArrowRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
      </Link>
    )
  }

  return (
    <Link
      href="/auth/signin"
      className="group inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm transition-all duration-300"
    >
      <Github className="h-4 w-4" />
      <span>Sign In</span>
      <ArrowRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
    </Link>
  )
}

export function AuthCTAButton({ size = "default" }: { size?: "default" | "large" }) {
  const { status } = useSession()
  const isSignedIn = status === "authenticated"
  const href = isSignedIn ? "/dashboard" : "/auth/signin"

  if (size === "large") {
    return (
      <Link
        href={href}
        className="group inline-flex items-center space-x-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 text-white font-bold text-xl shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
      >
        {isSignedIn ? <LayoutDashboard className="h-6 w-6" /> : <Github className="h-6 w-6" />}
        <span>{status === "loading" ? "..." : isSignedIn ? "Go to Dashboard" : "Get Started Free"}</span>
        <ArrowRight className="h-6 w-6 group-hover:translate-x-1 transition-transform" />
      </Link>
    )
  }

  return (
    <Link
      href={href}
      className="group inline-flex items-center space-x-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 text-white font-bold text-lg shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
    >
      <LayoutDashboard className="h-5 w-5" />
      <span>{status === "loading" ? "..." : isSignedIn ? "Go to Dashboard" : "Start Contributing Now"}</span>
      <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
    </Link>
  )
}
