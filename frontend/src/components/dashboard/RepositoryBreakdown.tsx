"use client"

import { motion } from "framer-motion"
import { GitFork, ExternalLink, FolderGit2 } from "lucide-react"

interface RepositoryBreakdownProps {
  contributions: Record<string, number>
}

export default function RepositoryBreakdown({ contributions }: RepositoryBreakdownProps) {
  const repos = Object.entries(contributions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  if (repos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <FolderGit2 className="h-10 w-10 mb-3 text-gray-600" />
        <p className="text-sm">No repository data yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {repos.map(([repo, count], i) => (
        <motion.a
          key={repo}
          href={`https://github.com/${repo}`}
          target="_blank"
          rel="noopener noreferrer"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.06 }}
          whileHover={{ x: 4 }}
          className="group flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-cyan-500/20 hover:bg-white/[0.05] transition-all duration-200"
        >
          <div className="flex items-center gap-3 min-w-0">
            <GitFork className="h-4 w-4 text-gray-500 group-hover:text-cyan-400 transition-colors shrink-0" />
            <span className="text-sm font-medium text-gray-300 group-hover:text-white truncate transition-colors">
              {repo}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs font-medium text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full">
              {count}
            </span>
            <ExternalLink className="h-3.5 w-3.5 text-gray-600 group-hover:text-cyan-400 transition-colors" />
          </div>
        </motion.a>
      ))}
    </div>
  )
}
