"use client"

import { motion } from "framer-motion"
import Link from "next/link"
import { ExternalLink, GitFork, Clock } from "lucide-react"
import { Issue } from "@/types/issue"

const DIFFICULTY_STYLES: Record<string, string> = {
  easy: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  hard: "bg-red-500/15 text-red-400 border-red-500/30",
}

const STATUS_STYLES: Record<string, string> = {
  available: "bg-cyan-500/15 text-cyan-400",
  claimed: "bg-purple-500/15 text-purple-400",
  completed: "bg-emerald-500/15 text-emerald-400",
  closed: "bg-gray-500/15 text-gray-400",
}

export default function IssueCard({ issue, index = 0 }: { issue: Issue; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/issues/${issue.id}`}>
        <div className="group bg-gradient-to-br from-white/[0.05] to-white/[0.01] border border-white/5 rounded-2xl p-5 hover:border-cyan-500/20 hover:bg-white/[0.06] transition-all duration-300 cursor-pointer">
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <h3 className="text-base font-semibold text-white group-hover:text-cyan-400 transition-colors line-clamp-1 flex-1">
              {issue.title}
            </h3>
            <span className={`shrink-0 px-2.5 py-1 rounded-full text-[11px] font-medium ${STATUS_STYLES[issue.status] || STATUS_STYLES.closed}`}>
              {issue.status}
            </span>
          </div>

          {/* Repo */}
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-3">
            <GitFork className="h-3.5 w-3.5" />
            <span>{issue.repository_full_name || issue.repository_name}</span>
          </div>

          {/* Description */}
          {issue.description && (
            <p className="text-sm text-gray-400 line-clamp-2 mb-4">{issue.description}</p>
          )}

          {/* Tags */}
          <div className="flex flex-wrap items-center gap-2">
            {issue.programming_language && (
              <span className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-blue-500/15 text-blue-400 border border-blue-500/20">
                {issue.programming_language}
              </span>
            )}
            {issue.difficulty_level && (
              <span className={`px-2.5 py-1 rounded-lg text-[11px] font-medium border ${DIFFICULTY_STYLES[issue.difficulty_level] || "bg-gray-500/15 text-gray-400 border-gray-500/20"}`}>
                {issue.difficulty_level}
              </span>
            )}
            {issue.labels.slice(0, 2).map((label) => (
              <span key={label} className="px-2.5 py-1 rounded-lg text-[11px] font-medium bg-white/5 text-gray-400 border border-white/10">
                {label}
              </span>
            ))}
            {issue.labels.length > 2 && (
              <span className="text-[11px] text-gray-600">+{issue.labels.length - 2}</span>
            )}
          </div>

          {/* Claimed info */}
          {issue.status === "claimed" && issue.claim_expires_at && (
            <div className="mt-4 pt-3 border-t border-white/5 flex items-center gap-1.5 text-xs text-gray-500">
              <Clock className="h-3.5 w-3.5" />
              Expires {new Date(issue.claim_expires_at).toLocaleDateString()}
            </div>
          )}

          {/* External link hint */}
          <div className="mt-3 flex justify-end">
            <ExternalLink className="h-3.5 w-3.5 text-gray-600 group-hover:text-cyan-400 transition-colors" />
          </div>
        </div>
      </Link>
    </motion.div>
  )
}
