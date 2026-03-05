"use client"

import { motion } from "framer-motion"
import { GitFork } from "lucide-react"

interface LanguageBreakdownProps {
  contributions: Record<string, number>
}

const LANG_COLORS: Record<string, string> = {
  Python: "from-blue-500 to-blue-400",
  JavaScript: "from-yellow-500 to-yellow-400",
  TypeScript: "from-blue-600 to-cyan-400",
  Go: "from-cyan-500 to-cyan-400",
  Rust: "from-orange-600 to-orange-400",
  Java: "from-red-500 to-red-400",
  "C++": "from-pink-500 to-pink-400",
  Ruby: "from-red-600 to-red-400",
  PHP: "from-purple-500 to-purple-400",
}

export default function LanguageBreakdown({ contributions }: LanguageBreakdownProps) {
  const languages = Object.entries(contributions).sort((a, b) => b[1] - a[1])
  const total = languages.reduce((sum, [, count]) => sum + count, 0)

  if (languages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <GitFork className="h-10 w-10 mb-3 text-gray-600" />
        <p className="text-sm">No language data yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {languages.map(([lang, count], i) => {
        const pct = (count / total) * 100
        const gradient = LANG_COLORS[lang] || "from-gray-500 to-gray-400"
        return (
          <motion.div
            key={lang}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm font-medium text-gray-300">{lang}</span>
              <span className="text-xs text-gray-500">
                {count} · {pct.toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.8, delay: i * 0.08 + 0.2 }}
                className={`h-full rounded-full bg-gradient-to-r ${gradient}`}
              />
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
