"use client"

import { motion } from "framer-motion"
import { Lock, CheckCircle2 } from "lucide-react"
import { UserAchievementProgress } from "@/types/dashboard"

interface AchievementBadgeProps {
  achievement: UserAchievementProgress
  index?: number
}

export default function AchievementBadge({ achievement, index = 0 }: AchievementBadgeProps) {
  const { achievement: details, progress, is_unlocked, percentage } = achievement

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      className={`relative p-4 rounded-2xl border transition-all duration-300 ${
        is_unlocked
          ? "border-cyan-500/30 bg-gradient-to-br from-cyan-500/10 to-blue-500/5"
          : "border-white/10 bg-white/[0.03] opacity-70"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="text-3xl shrink-0">{details.badge_icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className={`font-semibold text-sm truncate ${is_unlocked ? "text-white" : "text-gray-400"}`}>
              {details.name}
            </h4>
            {is_unlocked ? (
              <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0" />
            ) : (
              <Lock className="h-3.5 w-3.5 text-gray-500 shrink-0" />
            )}
          </div>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{details.description}</p>
          <div className="mt-2">
            <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
              <span>{progress} / {details.threshold}</span>
              <span>{Math.min(percentage, 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(percentage, 100)}%` }}
                transition={{ duration: 0.8, delay: index * 0.08 + 0.3 }}
                className={`h-full rounded-full ${
                  is_unlocked
                    ? "bg-gradient-to-r from-cyan-400 to-blue-500"
                    : "bg-gradient-to-r from-gray-500 to-gray-400"
                }`}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
