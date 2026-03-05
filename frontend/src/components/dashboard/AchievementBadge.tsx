"use client"

import { motion } from "framer-motion"
import { Lock, CheckCircle2, Trophy, Target, Rocket, Star, Flame, Zap, Crown, Shield, Medal, Globe, Code, Award } from "lucide-react"
import { UserAchievementProgress } from "@/types/dashboard"

const ACHIEVEMENT_STYLES: Record<string, { icon: typeof Trophy; gradient: string }> = {
  "First Steps":            { icon: Target,  gradient: "from-cyan-500 to-blue-500" },
  "Getting Started":        { icon: Rocket,  gradient: "from-emerald-500 to-cyan-500" },
  "Contributor":            { icon: Star,    gradient: "from-blue-500 to-purple-500" },
  "Active Contributor":     { icon: Flame,   gradient: "from-orange-500 to-red-500" },
  "Dedicated Developer":    { icon: Zap,     gradient: "from-yellow-500 to-amber-500" },
  "Merge Master":           { icon: Crown,   gradient: "from-amber-400 to-orange-500" },
  "Open Source Hero":       { icon: Shield,  gradient: "from-purple-500 to-pink-500" },
  "Century Club":           { icon: Medal,   gradient: "from-amber-300 to-yellow-500" },
  "Python Pioneer":         { icon: Code,    gradient: "from-blue-400 to-yellow-400" },
  "JavaScript Journeyman":  { icon: Code,    gradient: "from-yellow-400 to-amber-500" },
  "TypeScript Titan":       { icon: Code,    gradient: "from-blue-500 to-blue-700" },
  "Go Guru":                { icon: Code,    gradient: "from-cyan-400 to-blue-500" },
  "Rust Ranger":            { icon: Code,    gradient: "from-orange-400 to-red-600" },
  "Polyglot":               { icon: Globe,   gradient: "from-emerald-400 to-teal-500" },
}
const DEFAULT_STYLE = { icon: Award, gradient: "from-gray-500 to-gray-600" }

interface AchievementBadgeProps {
  achievement: UserAchievementProgress
  index?: number
}

export default function AchievementBadge({ achievement, index = 0 }: AchievementBadgeProps) {
  const { achievement: details, progress, is_unlocked, percentage } = achievement
  const style = ACHIEVEMENT_STYLES[details.name] || DEFAULT_STYLE
  const Icon = style.icon

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
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
          is_unlocked
            ? `bg-gradient-to-br ${style.gradient} shadow-lg`
            : "bg-white/5 border border-white/10"
        }`}>
          {is_unlocked ? (
            <Icon className="h-5 w-5 text-white" />
          ) : (
            <Lock className="h-4 w-4 text-gray-600" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className={`font-semibold text-sm truncate ${is_unlocked ? "text-white" : "text-gray-400"}`}>
              {details.name}
            </h4>
            {is_unlocked && <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0" />}
          </div>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{details.description}</p>
          <div className="mt-2">
            <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
              <span>{progress} / {details.threshold}</span>
            </div>
            <div className="w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(percentage, 100)}%` }}
                transition={{ duration: 0.8, delay: index * 0.08 + 0.3 }}
                className={`h-full rounded-full ${
                  is_unlocked
                    ? `bg-gradient-to-r ${style.gradient}`
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
