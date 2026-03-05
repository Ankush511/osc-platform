"use client"

import { useState, useEffect } from "react"
import { Search, X } from "lucide-react"

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  debounceMs?: number
}

export default function SearchBar({ value, onChange, debounceMs = 500 }: SearchBarProps) {
  const [local, setLocal] = useState(value)

  useEffect(() => setLocal(value), [value])

  useEffect(() => {
    const t = setTimeout(() => { if (local !== value) onChange(local) }, debounceMs)
    return () => clearTimeout(t)
  }, [local, value, onChange, debounceMs])

  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-500" />
      </div>
      <input
        type="text"
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder="Search issues by title or description..."
        className="block w-full pl-12 pr-10 py-3.5 bg-white/[0.05] border border-white/10 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 text-sm transition-all"
      />
      {local && (
        <button
          onClick={() => { setLocal(""); onChange("") }}
          className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-white transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
