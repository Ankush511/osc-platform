"use client"

import { useState, useEffect, useCallback } from "react"
import { motion } from "framer-motion"
import { Sparkles, SlidersHorizontal, X } from "lucide-react"
import { IssueFilters, AvailableFilters, PaginatedIssuesResponse } from "@/types/issue"
import { fetchIssues } from "@/lib/issues-api"
import IssueList from "./IssueList"
import FilterSidebar from "./FilterSidebar"
import SearchBar from "./SearchBar"

interface Props {
  availableFilters: AvailableFilters | null
}

export default function IssueDiscoveryClient({ availableFilters }: Props) {
  const [filters, setFilters] = useState<IssueFilters>({ status: "available" })
  const [searchQuery, setSearchQuery] = useState("")
  const [page, setPage] = useState(1)
  const [issuesData, setIssuesData] = useState<PaginatedIssuesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const loadIssues = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchIssues({
        page,
        page_size: 20,
        filters: { ...filters, search_query: searchQuery || undefined },
      })
      setIssuesData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load issues")
    } finally {
      setLoading(false)
    }
  }, [page, filters, searchQuery])

  useEffect(() => { loadIssues() }, [loadIssues])

  return (
    <div>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 mb-4">
          <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
          <span className="text-xs text-cyan-300 font-medium">Beginner-friendly issues</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white mb-2">
          Discover <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Open Source Issues</span>
        </h1>
        <p className="text-gray-400">Find your next contribution and start building your portfolio</p>
      </motion.div>

      {/* Search */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-6">
        <SearchBar value={searchQuery} onChange={(q) => { setSearchQuery(q); setPage(1) }} />
      </motion.div>

      {/* Mobile filter toggle */}
      <div className="lg:hidden mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all"
        >
          {showFilters ? <X className="h-4 w-4" /> : <SlidersHorizontal className="h-4 w-4" />}
          {showFilters ? "Hide Filters" : "Show Filters"}
        </button>
      </div>

      {/* Main grid */}
      <div className="flex flex-col lg:flex-row gap-6">
        <aside className={`lg:block ${showFilters ? "block" : "hidden"} lg:w-64 shrink-0`}>
          <FilterSidebar filters={filters} availableFilters={availableFilters} onFilterChange={(f) => { setFilters(f); setPage(1) }} />
        </aside>
        <div className="flex-1">
          <IssueList issuesData={issuesData} loading={loading} error={error} currentPage={page} onPageChange={(p) => { setPage(p); window.scrollTo({ top: 0, behavior: "smooth" }) }} />
        </div>
      </div>
    </div>
  )
}
