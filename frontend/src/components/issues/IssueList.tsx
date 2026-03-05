"use client"

import { motion } from "framer-motion"
import { Search, AlertTriangle, Loader2 } from "lucide-react"
import { PaginatedIssuesResponse } from "@/types/issue"
import IssueCard from "./IssueCard"
import Pagination from "./Pagination"

interface Props {
  issuesData: PaginatedIssuesResponse | null
  loading: boolean
  error: string | null
  currentPage: number
  onPageChange: (page: number) => void
}

export default function IssueList({ issuesData, loading, error, currentPage, onPageChange }: Props) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white/[0.03] border border-white/5 rounded-2xl p-5 animate-pulse">
            <div className="h-5 bg-white/10 rounded-lg w-3/4 mb-3" />
            <div className="h-3 bg-white/5 rounded w-1/3 mb-4" />
            <div className="h-4 bg-white/5 rounded w-2/3" />
          </div>
        ))}
        <div className="flex justify-center pt-4">
          <Loader2 className="h-5 w-5 text-cyan-400 animate-spin" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
        <AlertTriangle className="h-10 w-10 text-red-400 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-white mb-1">Error loading issues</h3>
        <p className="text-red-300 text-sm">{error}</p>
      </div>
    )
  }

  if (!issuesData || issuesData.items.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] border border-white/10 rounded-2xl p-12 text-center"
      >
        <Search className="h-12 w-12 text-gray-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">No issues found</h3>
        <p className="text-gray-400 text-sm">Try adjusting your filters or search query</p>
      </motion.div>
    )
  }

  return (
    <div>
      <p className="text-xs text-gray-500 mb-4">
        Showing {issuesData.items.length} of {issuesData.total} issues
      </p>
      <div className="space-y-3 mb-6">
        {issuesData.items.map((issue, i) => (
          <IssueCard key={issue.id} issue={issue} index={i} />
        ))}
      </div>
      {issuesData.total_pages > 1 && (
        <Pagination currentPage={currentPage} totalPages={issuesData.total_pages} onPageChange={onPageChange} />
      )}
    </div>
  )
}
