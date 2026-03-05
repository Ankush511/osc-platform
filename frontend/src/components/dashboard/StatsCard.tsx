"use client"

import { motion } from "framer-motion"
import { BarChart3, GitPullRequest, GitMerge, Trophy } from "lucide-react"

const ICONS = {
  BarChart3,
  GitPullRequest,
  GitMerge,
  Trophy,
} as const

interface StatsCardProps {
  title: string
  value: number | string
  iconName: keyof typeof ICONS
  description?: string
  index?: number
}

export default function StatsCard({ title, value, iconName, description, index = 0 }: StatsCardProps) {
  const Icon = ICONS[iconName]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={{ y: -4, scale: 1.02 }}
      className="group relative"
    >
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      <div className="relative bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:border-cyan-500/30 transition-all duration-300">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 group-hover:scale-110 transition-transform duration-300">
            <Icon className="h-6 w-6 text-cyan-400" />
          </div>
        </div>
        <div className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-1">
          {value}
        </div>
        <p className="text-sm font-medium text-gray-400">{title}</p>
        {description && (
          <p className="text-xs text-gray-500 mt-1">{description}</p>
        )}
      </div>
    </motion.div>
  )
}
