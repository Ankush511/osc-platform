"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { GitMerge, Clock, XCircle, ExternalLink, Filter } from "lucide-react"
import { RecentContribution } from "@/types/dashboard"

interface ContributionTimelineProps {
  contributions: RecentContribution[]
}

const STATUS_CONFIG = {
  merged: { icon: GitMerge, color: "text-emerald-400", bg: "bg-emerald-500", label: "Merged" },
  submitted: { icon: Clock, color: "text-cyan-400", bg: "bg-cyan-500", label: "Pending" },
  closed: { icon: XCircle, color: "text-gray-400", bg: "bg-gray-500", label: "Closed" },
} as const

const FILTERS = [
  { key: "all", label: "All" },
  { key: "merged", label: "Merged" },
  { key: "submitted", label: "Pending" },
  { key: "closed", label: "Closed" },
]

export default function ContributionTimeline({ contributions }: ContributionTimelineProps) {
  const [filter, setFilter] = useState("all")

  const filtered = filter === "all" ? contributions : contributions.filter(c => c.status === filter)

  const formatDate = (d: string) =>
    new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric" })

  if (contributions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <GitMerge className="h-10 w-10 mb-3 text-gray-600" />
        <p className="text-sm">No contributions yet. Start your journey!</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center gap-2 mb-5">
        <Filter className="h-3.5 w-3.5 text-gray-500" />
        {FILTERS.map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              filter === f.key
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25"
                : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="popLayout">
        {filtered.length === 0 ? (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8 text-gray-500 text-sm"
          >
            No {filter} contributions
          </motion.p>
        ) : (
          <div className="space-y-3">
            {filtered.map((c, i) => {
              const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.closed
              const Icon = cfg.icon
              return (
                <motion.div
                  key={c.contribution_id}
                  layout
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ delay: i * 0.05 }}
                  className="group flex items-start gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-cyan-500/20 hover:bg-white/[0.05] transition-all duration-200"
                >
                  <div className={`flex items-center justify-center w-8 h-8 rounded-lg ${cfg.bg}/20 shrink-0 mt-0.5`}>
                    <Icon className={`h-4 w-4 ${cfg.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{c.issue_title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{c.repository}</p>
                  </div>
                  <div className="flex flex-col items-end gap-1 shrink-0">
                    <span className="text-[10px] text-gray-500">{formatDate(c.submitted_at)}</span>
                    <a
                      href={c.pr_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
