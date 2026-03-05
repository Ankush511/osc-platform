"use client"

import { GitPullRequestArrow } from "lucide-react"

interface LogoIconProps {
  size?: "sm" | "md" | "lg"
}

const SIZES = {
  sm: { outer: "p-2 rounded-lg", icon: "h-6 w-6" },
  md: { outer: "p-2.5 rounded-xl", icon: "h-7 w-7" },
  lg: { outer: "p-3.5 rounded-2xl", icon: "h-9 w-9" },
}

export function LogoIcon({ size = "md" }: LogoIconProps) {
  const s = SIZES[size]
  return (
    <div className={`relative bg-gradient-to-br from-cyan-500 to-blue-600 ${s.outer} flex items-center justify-center`}>
      <GitPullRequestArrow className={`${s.icon} text-white`} strokeWidth={2.5} />
    </div>
  )
}

export function LogoWithGlow({ size = "md" }: LogoIconProps) {
  return (
    <div className="relative">
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
      <LogoIcon size={size} />
    </div>
  )
}
