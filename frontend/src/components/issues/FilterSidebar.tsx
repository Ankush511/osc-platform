"use client"

import { useState, useMemo } from "react"
import { IssueFilters, AvailableFilters } from "@/types/issue"
import { X, Search, ChevronDown, Tag } from "lucide-react"

const DEFAULT_LABELS = [
  "good first issue",
  "bug",
  "hacktoberfest",
  "help wanted",
  "priority:high",
  "priority:low",
  "priority:medium",
  "feature request",
  "feature-request",
  "documentation",
]

const DIFFICULTY_OPTIONS = [
  { value: "easy", label: "Easy", color: "text-emerald-400 bg-emerald-500/15 border-emerald-500/30" },
  { value: "medium", label: "Medium", color: "text-yellow-400 bg-yellow-500/15 border-yellow-500/30" },
  { value: "hard", label: "Hard", color: "text-red-400 bg-red-500/15 border-red-500/30" },
]

const STATUS_OPTIONS = [
  { value: "available", label: "Unclaimed", color: "text-emerald-400 bg-emerald-500/15 border-emerald-500/30" },
  { value: "claimed", label: "Claimed", color: "text-amber-400 bg-amber-500/15 border-amber-500/30" },
  { value: "completed", label: "Completed", color: "text-cyan-400 bg-cyan-500/15 border-cyan-500/30" },
]

const DEFAULT_LANGUAGES = [
  "JavaScript", "TypeScript", "Python", "Java", "Go", "Rust",
  "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Dart", "Scala", "C", "Shell",
]

interface Props {
  filters: IssueFilters
  availableFilters: AvailableFilters | null
  onFilterChange: (filters: IssueFilters) => void
}

export default function FilterSidebar({ filters, availableFilters, onFilterChange }: Props) {
  const [labelSearch, setLabelSearch] = useState("")
  const [langOpen, setLangOpen] = useState(false)

  // Merge API languages with defaults, deduplicate
  const languages = useMemo(() => {
    const apiLangs = availableFilters?.programming_languages || []
    const merged = new Set([...DEFAULT_LANGUAGES, ...apiLangs])
    return Array.from(merged).sort()
  }, [availableFilters])

  // Merge default labels with available labels from API, deduplicate
  const allLabels = useMemo(() => {
    const apiLabels = availableFilters?.labels || []
    const merged = new Set([...DEFAULT_LABELS, ...apiLabels.map(l => l.toLowerCase())])
    return Array.from(merged).sort()
  }, [availableFilters])

  const filteredLabels = useMemo(() => {
    if (!labelSearch) return allLabels.slice(0, 12) // show first 12 by default
    return allLabels.filter(l => l.toLowerCase().includes(labelSearch.toLowerCase()))
  }, [allLabels, labelSearch])

  const toggleFilter = (key: "programming_languages" | "labels" | "difficulty_levels", val: string) => {
    const current = filters[key] || []
    const updated = current.includes(val) ? current.filter(v => v !== val) : [...current, val]
    onFilterChange({ ...filters, [key]: updated.length ? updated : undefined })
  }

  const setLanguage = (lang: string) => {
    const current = filters.programming_languages || []
    const updated = current.includes(lang) ? current.filter(l => l !== lang) : [...current, lang]
    onFilterChange({ ...filters, programming_languages: updated.length ? updated : undefined })
    setLangOpen(false)
  }

  const hasActive =
    (filters.programming_languages?.length || 0) > 0 ||
    (filters.labels?.length || 0) > 0 ||
    (filters.difficulty_levels?.length || 0) > 0 ||
    !!filters.status

  return (
    <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-5 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-white">Filters</h3>
        {hasActive && (
          <button onClick={() => onFilterChange({})} className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors">
            <X className="h-3 w-3" /> Clear all
          </button>
        )}
      </div>

      {/* Active filters */}
      {hasActive && (
        <div className="flex flex-wrap gap-1.5">
          {filters.programming_languages?.map(l => (
            <span key={`lang-${l}`} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-blue-500/15 text-blue-400 border border-blue-500/20">
              {l}
              <button onClick={() => toggleFilter("programming_languages", l)}><X className="h-3 w-3" /></button>
            </span>
          ))}
          {filters.labels?.map(l => (
            <span key={`label-${l}`} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-purple-500/15 text-purple-400 border border-purple-500/20">
              {l}
              <button onClick={() => toggleFilter("labels", l)}><X className="h-3 w-3" /></button>
            </span>
          ))}
          {filters.difficulty_levels?.map(d => (
            <span key={`diff-${d}`} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-cyan-500/15 text-cyan-400 border border-cyan-500/20">
              {d}
              <button onClick={() => toggleFilter("difficulty_levels", d)}><X className="h-3 w-3" /></button>
            </span>
          ))}
          {filters.status && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-amber-500/15 text-amber-400 border border-amber-500/20">
              {STATUS_OPTIONS.find(o => o.value === filters.status)?.label || filters.status}
              <button onClick={() => onFilterChange({ ...filters, status: undefined })}><X className="h-3 w-3" /></button>
            </span>
          )}
        </div>
      )}

      {/* Language Dropdown */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Language</h4>
        <div className="relative">
          <button
            onClick={() => setLangOpen(!langOpen)}
            className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl bg-white/[0.05] border border-white/10 text-sm text-gray-300 hover:border-cyan-500/30 transition-all"
          >
            <span>{filters.programming_languages?.length ? filters.programming_languages.join(", ") : "All languages"}</span>
            <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${langOpen ? "rotate-180" : ""}`} />
          </button>
          {langOpen && (
            <div className="absolute z-20 mt-1 w-full bg-[#0d1117] border border-white/10 rounded-xl shadow-2xl shadow-black/50 max-h-64 overflow-y-auto">
              <button
                onClick={() => { onFilterChange({ ...filters, programming_languages: undefined }); setLangOpen(false) }}
                className={`w-full text-left px-3 py-2 text-sm transition-colors ${!filters.programming_languages?.length ? "text-cyan-400 bg-cyan-500/10" : "text-gray-400 hover:bg-white/5"}`}
              >
                All languages
              </button>
              {languages.map(lang => (
                <button
                  key={lang}
                  onClick={() => setLanguage(lang)}
                  className={`w-full text-left px-3 py-2 text-sm transition-colors ${filters.programming_languages?.includes(lang) ? "text-cyan-400 bg-cyan-500/10" : "text-gray-400 hover:bg-white/5"}`}
                >
                  {lang}
                </button>
              ))}
              {languages.length === 0 && (
                <p className="px-3 py-2 text-xs text-gray-600">No languages available</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Labels with search */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Labels</h4>
        <div className="relative mb-2">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-500" />
          <input
            type="text"
            value={labelSearch}
            onChange={e => setLabelSearch(e.target.value)}
            placeholder="Search labels..."
            className="w-full pl-8 pr-3 py-2 rounded-lg bg-white/[0.05] border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/30 transition-all"
          />
        </div>
        <div className="space-y-1 max-h-52 overflow-y-auto pr-1 scrollbar-thin">
          {filteredLabels.map(label => {
            const active = filters.labels?.includes(label)
            return (
              <button
                key={label}
                onClick={() => toggleFilter("labels", label)}
                className={`w-full flex items-center gap-2 text-left px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                  active
                    ? "bg-purple-500/15 text-purple-300 border border-purple-500/30"
                    : "text-gray-400 hover:bg-white/5 hover:text-white border border-transparent"
                }`}
              >
                <Tag className="h-3 w-3 shrink-0" />
                <span className="truncate">{label}</span>
              </button>
            )
          })}
          {filteredLabels.length === 0 && (
            <p className="text-xs text-gray-600 py-2 text-center">No matching labels</p>
          )}
        </div>
      </div>

      {/* Difficulty */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Difficulty</h4>
        <div className="flex flex-wrap gap-2">
          {DIFFICULTY_OPTIONS.map(opt => {
            const active = filters.difficulty_levels?.includes(opt.value)
            return (
              <button
                key={opt.value}
                onClick={() => toggleFilter("difficulty_levels", opt.value)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  active ? opt.color : "text-gray-400 bg-white/[0.03] border-white/10 hover:bg-white/5"
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Status */}
      <div>
        <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Status</h4>
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map(opt => {
            const active = filters.status === opt.value
            return (
              <button
                key={opt.value}
                onClick={() => onFilterChange({ ...filters, status: active ? undefined : opt.value as IssueFilters["status"] })}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  active ? opt.color : "text-gray-400 bg-white/[0.03] border-white/10 hover:bg-white/5"
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
