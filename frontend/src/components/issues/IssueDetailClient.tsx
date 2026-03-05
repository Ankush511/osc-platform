"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useRouter } from "next/navigation"
import {
  Sparkles, GitFork, ExternalLink, Tag, Clock, Rocket,
  BookOpen, GraduationCap, AlertTriangle, Undo2,
  CalendarPlus, Zap, ChevronDown, ChevronUp, Brain,
  ShieldCheck, CheckCircle2, GitPullRequest, Info,
} from "lucide-react"
import { Issue } from "@/types/issue"
import { IssueExplanationResponse } from "@/types/ai"
import { claimIssue, releaseIssue, extendClaimDeadline, submitPullRequest, simulatePR } from "@/lib/issues-api"
import { fetchIssueExplanation } from "@/lib/ai-api"
import Markdown from "@/components/ui/Markdown"

const DIFF: Record<string, { cls: string; label: string }> = {
  easy: { cls: "text-emerald-400 bg-emerald-500/15 border-emerald-500/30", label: "Easy" },
  medium: { cls: "text-yellow-400 bg-yellow-500/15 border-yellow-500/30", label: "Medium" },
  hard: { cls: "text-red-400 bg-red-500/15 border-red-500/30", label: "Hard" },
  unknown: { cls: "text-gray-400 bg-gray-500/15 border-gray-500/20", label: "Unknown" },
}

function PulsingDots() {
  return (
    <span className="inline-flex gap-1 ml-1">
      {[0, 1, 2].map(i => (
        <motion.span key={i} className="w-1.5 h-1.5 rounded-full bg-cyan-400"
          animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }} />
      ))}
    </span>
  )
}

interface Props {
  issue: Issue
  accessToken: string
  currentUserId: number
}

export default function IssueDetailClient({ issue: initialIssue, accessToken, currentUserId: initialUserId }: Props) {
  const router = useRouter()
  const [issue, setIssue] = useState(initialIssue)
  const [userId, setUserId] = useState(initialUserId)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [descExpanded, setDescExpanded] = useState(false)
  const [aiData, setAiData] = useState<IssueExplanationResponse | null>(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState<string | null>(null)

  // If the issue already has a cached AI explanation, show it immediately
  const hasCachedExplanation = !!issue.ai_explanation && !aiData
  const [showExtend, setShowExtend] = useState(false)
  const [extDays, setExtDays] = useState(7)
  const [justification, setJustification] = useState("")
  const [showAgreement, setShowAgreement] = useState(false)
  const [agreedTerms, setAgreedTerms] = useState(false)
  const [showRelease, setShowRelease] = useState(false)
  const [releaseReason, setReleaseReason] = useState("")
  const [showSubmitPR, setShowSubmitPR] = useState(false)
  const [prUrl, setPrUrl] = useState("")
  const [prSubmitted, setPrSubmitted] = useState(false)
  const [prResult, setPrResult] = useState<{ points_earned?: number; pr_number?: number; achievements?: string[] } | null>(null)

  // Fetch the real DB user ID client-side to ensure isMine works correctly
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data?.id) setUserId(data.id) })
      .catch(() => {})
  }, [accessToken])

  const isMine = issue.claimed_by === userId
  const isOther = !!issue.claimed_by && issue.claimed_by !== userId
  const diff = DIFF[issue.difficulty_level || "unknown"] || DIFF.unknown

  const act = async (fn: () => Promise<void>) => {
    setLoading(true); setError(null)
    try { await fn() } catch (e: unknown) { setError(e instanceof Error ? e.message : "Something went wrong") }
    finally { setLoading(false) }
  }
  const handleClaim = () => act(async () => {
    const r = await claimIssue(issue.id, accessToken)
    if (r.success) {
      setIssue({ ...issue, status: "claimed", claimed_by: userId, claimed_at: r.claimed_at || new Date().toISOString(), claim_expires_at: r.claim_expires_at || null })
      setShowAgreement(true)
    }
  })
  const handleAcceptAgreement = () => {
    setShowAgreement(false)
    setAgreedTerms(false)
    window.open(issue.github_url, "_blank")
  }
  const handleRelease = () => act(async () => {
    const r = await releaseIssue(issue.id, accessToken, releaseReason || undefined)
    if (r.success) { setIssue({ ...issue, status: "available", claimed_by: null, claimed_at: null, claim_expires_at: null }); setShowRelease(false); setReleaseReason("") }
  })
  const handleExtend = () => act(async () => {
    if (justification.length < 10) { setError("Justification needs at least 10 characters"); return }
    const r = await extendClaimDeadline(issue.id, extDays, justification, accessToken)
    if (r.success) { setIssue({ ...issue, claim_expires_at: r.new_expiration || issue.claim_expires_at }); setShowExtend(false); setJustification(""); setError(null) }
    else { setError(r.message || "Failed to extend deadline") }
  })
  const handleSubmitPR = () => act(async () => {
    if (!prUrl.trim()) { setError("Please enter a PR URL"); return }
    const r = await submitPullRequest(issue.id, prUrl.trim(), accessToken)
    setPrSubmitted(true)
    setPrResult({ points_earned: r.points_earned, pr_number: r.pr_number })
    setIssue({ ...issue, status: "completed" })
    setError(null)
  })
  const handleSimulatePR = (merge: boolean) => act(async () => {
    const r = await simulatePR(issue.id, merge, accessToken)
    setPrSubmitted(true)
    setPrResult({ points_earned: r.points_earned, pr_number: r.contribution_id, achievements: r.achievements_earned })
    setIssue({ ...issue, status: "completed" })
    setShowSubmitPR(true)
    setError(null)
  })
  const handleGenerateAI = async () => {
    setAiLoading(true); setAiError(null)
    try { const data = await fetchIssueExplanation(issue.id, accessToken); setAiData(data) }
    catch (e: unknown) { setAiError(e instanceof Error ? e.message : "Failed to generate AI summary") }
    finally { setAiLoading(false) }
  }

  return (
    <div className="space-y-6">
      {error && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
        </motion.div>
      )}

      {/* Top row: issue header + sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Issue header */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-start justify-between gap-4 mb-3">
              <h1 className="text-xl sm:text-2xl font-black text-white leading-tight">{issue.title}</h1>
              <span className={`shrink-0 px-3 py-1.5 rounded-xl text-xs font-semibold border ${diff.cls}`}>{diff.label}</span>
            </div>
            <div className="flex items-center gap-2 mb-4">
              <GitFork className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-400">{issue.repository_full_name}</span>
              {issue.programming_language && (
                <span className="text-xs font-medium text-blue-400 bg-blue-500/15 px-2 py-0.5 rounded-full border border-blue-500/20 ml-1">{issue.programming_language}</span>
              )}
            </div>
            {issue.labels.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-4">
                {issue.labels.map(l => (
                  <span key={l} className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-medium bg-white/5 text-gray-400 border border-white/10">
                    <Tag className="h-2.5 w-2.5" /> {l}
                  </span>
                ))}
              </div>
            )}
            <div className="flex flex-wrap gap-2 pt-3 border-t border-white/5">
              {issue.status === "available" && (
                <button onClick={handleClaim} disabled={loading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 transition-all shadow-lg shadow-cyan-500/20">
                  <Rocket className="h-4 w-4" /> Solve It
                </button>
              )}
              {isMine && issue.status === "claimed" && (
                <>
                  <button onClick={() => { setError(null); setShowSubmitPR(true) }}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-600 text-white font-semibold text-sm hover:from-emerald-400 hover:to-cyan-500 transition-all shadow-lg shadow-emerald-500/20">
                    <GitPullRequest className="h-4 w-4" /> Submit PR
                  </button>
                  <a href={issue.github_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all"><ExternalLink className="h-4 w-4" /> GitHub</a>
                  <button onClick={() => setShowRelease(true)} disabled={loading} className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all"><Undo2 className="h-4 w-4" /> Release</button>
                  <button onClick={() => { setError(null); setShowExtend(true) }} className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all"><CalendarPlus className="h-4 w-4" /> Extend</button>
                </>
              )}
              {issue.status === "completed" && (
                <div className="flex items-center gap-3 w-full">
                  <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
                    <CheckCircle2 className="h-4 w-4" /> PR Submitted
                  </div>
                  <a href={issue.github_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all"><ExternalLink className="h-4 w-4" /> View on GitHub</a>
                </div>
              )}
              {(issue.status === "available" || isOther) && (
                <a href={issue.github_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all"><ExternalLink className="h-4 w-4" /> View on GitHub</a>
              )}
            </div>
          </motion.div>

          {/* Description — collapsible */}
          {issue.description && (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
              className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl overflow-hidden">
              <button onClick={() => setDescExpanded(!descExpanded)} className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-white/[0.02] transition-colors">
                <span className="text-sm font-semibold text-white">Issue Description</span>
                {descExpanded ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />}
              </button>
              <AnimatePresence>
                {descExpanded && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                    <div className="px-6 pb-6 max-h-[500px] overflow-y-auto"><Markdown content={issue.description} /></div>
                  </motion.div>
                )}
              </AnimatePresence>
              {!descExpanded && <div className="px-6 pb-4"><p className="text-gray-500 text-xs line-clamp-3">{issue.description.slice(0, 300)}...</p></div>}
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {issue.status === "claimed" && (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              className="bg-gradient-to-br from-blue-500/[0.06] to-purple-500/[0.03] backdrop-blur-sm border border-blue-500/15 rounded-2xl p-5">
              <div className="flex items-center gap-3 mb-2"><Clock className="h-5 w-5 text-blue-400" /><span className="text-sm font-semibold text-white">{isMine ? "You claimed this" : "Claimed"}</span></div>
              {issue.claim_expires_at && <p className="text-xs text-gray-400">Expires {new Date(issue.claim_expires_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" })}</p>}
            </motion.div>
          )}
          {issue.status === "completed" && (
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              className="bg-gradient-to-br from-emerald-500/[0.06] to-cyan-500/[0.03] backdrop-blur-sm border border-emerald-500/15 rounded-2xl p-5">
              <div className="flex items-center gap-3 mb-2"><CheckCircle2 className="h-5 w-5 text-emerald-400" /><span className="text-sm font-semibold text-white">Completed</span></div>
              <p className="text-xs text-gray-400">A pull request has been submitted for this issue.</p>
            </motion.div>
          )}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-5 space-y-3">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Details</h4>
            <div className="space-y-2.5 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Status</span><span className="text-white capitalize">{issue.status}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Language</span><span className="text-white">{issue.programming_language || "—"}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Difficulty</span><span className={`${diff.cls} px-2 py-0.5 rounded text-xs border`}>{diff.label}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Labels</span><span className="text-white">{issue.labels.length}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Repo</span><span className="text-cyan-400 text-xs truncate ml-2">{issue.repository_full_name}</span></div>
            </div>
          </motion.div>
          <button onClick={() => router.push("/issues")} className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-400 text-sm font-medium hover:bg-white/10 hover:text-white transition-all text-center">← Back to Issues</button>
        </div>
      </div>

      {/* AI Summary — FULL WIDTH below the grid */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="bg-gradient-to-br from-cyan-500/[0.04] to-blue-500/[0.02] backdrop-blur-sm border border-cyan-500/10 rounded-2xl p-8">

        {/* Not generated yet */}
        {!aiData && !aiLoading && !aiError && !hasCachedExplanation && (
          <div className="text-center py-10">
            <motion.div animate={{ rotate: [0, 5, -5, 0] }} transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 mb-5">
              <Brain className="h-8 w-8 text-cyan-400" />
            </motion.div>
            <h3 className="text-xl font-bold text-white mb-2">AI-Powered Summary</h3>
            {(issue.status === "completed" || issue.status === "closed") ? (
              <>
                <p className="text-gray-400 text-sm mb-6 max-w-lg mx-auto leading-relaxed">
                  This issue has been completed. You can still generate an AI summary to learn from it — understand what was involved, key concepts, and the approach taken.
                </p>
                <button onClick={handleGenerateAI}
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 font-medium text-sm hover:bg-white/10 hover:text-white transition-all">
                  <Sparkles className="h-4 w-4" /> Generate Summary to Learn
                </button>
              </>
            ) : (
              <>
                <p className="text-gray-400 text-sm mb-6 max-w-lg mx-auto leading-relaxed">
                  Get a beginner-friendly explanation of this issue — what needs to be done, key concepts, suggested approach, and learning resources.
                </p>
                <button onClick={handleGenerateAI}
                  className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 transition-all">
                  <Sparkles className="h-4 w-4" /> Generate AI Summary
                </button>
              </>
            )}
          </div>
        )}

        {/* Cached explanation from database */}
        {!aiData && !aiLoading && hasCachedExplanation && (
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                <Sparkles className="h-5 w-5 text-cyan-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white">AI Explanation</h3>
                <p className="text-[11px] text-gray-500">Powered by AI on AWS Bedrock</p>
              </div>
            </div>
            <div className="bg-white/[0.02] rounded-xl p-6 sm:p-8 border border-white/5 leading-relaxed">
              <Markdown content={issue.ai_explanation!} className="text-[15px]" />
            </div>
          </div>
        )}

        {/* Loading */}
        {aiLoading && (
          <div className="text-center py-14">
            <div className="relative inline-flex items-center justify-center w-20 h-20 mb-6">
              <motion.div className="absolute inset-0 rounded-full border-2 border-cyan-500/20"
                animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.2, 0.5] }} transition={{ duration: 2, repeat: Infinity }} />
              <motion.div className="absolute inset-2 rounded-full border-2 border-cyan-400/30"
                animate={{ rotate: 360 }} transition={{ duration: 3, repeat: Infinity, ease: "linear" }} />
              <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 1.5, repeat: Infinity }}>
                <Sparkles className="h-8 w-8 text-cyan-400" />
              </motion.div>
            </div>
            <h3 className="text-xl font-bold text-white mb-1">Generating Summary <PulsingDots /></h3>
            <p className="text-gray-500 text-sm italic">Generation time depends on the issue length and typically takes 20–30 seconds.</p>
            <div className="mt-5 max-w-sm mx-auto">
              <motion.div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <motion.div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                  animate={{ x: ["-100%", "100%"] }} transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }} style={{ width: "40%" }} />
              </motion.div>
            </div>
          </div>
        )}

        {/* Error */}
        {aiError && !aiLoading && (
          <div className="text-center py-10">
            <AlertTriangle className="h-10 w-10 text-red-400 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white mb-1">Failed to generate summary</h3>
            <p className="text-gray-400 text-sm mb-4">{aiError}</p>
            <button onClick={handleGenerateAI}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm hover:bg-white/10 transition-all">
              <Sparkles className="h-4 w-4" /> Try Again
            </button>
          </div>
        )}

        {/* AI Result */}
        {aiData && !aiLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                <Sparkles className="h-5 w-5 text-cyan-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white">AI Explanation</h3>
                <p className="text-[11px] text-gray-500">Powered by AI on AWS Bedrock</p>
              </div>
              {aiData.difficulty_level && (
                <span className={`px-3 py-1 rounded-lg text-xs font-medium border flex items-center gap-1.5 ${(DIFF[aiData.difficulty_level] || DIFF.unknown).cls}`}>
                  <Zap className="h-3 w-3" /> AI assessed: {(DIFF[aiData.difficulty_level] || DIFF.unknown).label}
                </span>
              )}
            </div>

            {/* Explanation content */}
            <div className="bg-white/[0.02] rounded-xl p-6 sm:p-8 border border-white/5 leading-relaxed">
              <Markdown content={aiData.explanation} className="text-[15px]" />
            </div>

            {/* Learning resources */}
            {aiData.learning_resources && aiData.learning_resources.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <GraduationCap className="h-4 w-4 text-cyan-400" />
                  <span className="text-sm font-bold text-white">Learning Resources</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {aiData.learning_resources.map((r, i) => (
                    <a key={i} href={r.url} target="_blank" rel="noopener noreferrer"
                      className="flex items-start gap-3 p-4 rounded-xl bg-white/[0.03] border border-white/5 hover:border-cyan-500/20 hover:bg-white/[0.06] transition-all group">
                      <BookOpen className="h-4 w-4 text-gray-600 group-hover:text-cyan-400 mt-0.5 shrink-0 transition-colors" />
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-gray-300 group-hover:text-white transition-colors">{r.title}</p>
                        {r.description && <p className="text-[11px] text-gray-500 mt-1 line-clamp-2">{r.description}</p>}
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            )}

          </motion.div>
        )}
      </motion.div>

      {/* Extend Modal */}
      <AnimatePresence>
        {showExtend && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }} exit={{ scale: 0.95 }}
              className="bg-[#0d1117] border border-white/10 rounded-2xl p-6 max-w-md w-full">
              <h3 className="text-lg font-bold text-white mb-4">Extend Deadline</h3>
              {error && (
                <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
                </div>
              )}
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-400 mb-1.5">Days (1–14)</label>
                <input type="number" min={1} max={14} value={extDays} onChange={e => setExtDays(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:border-cyan-500/50" />
              </div>
              <div className="mb-5">
                <label className="block text-xs font-medium text-gray-400 mb-1.5">Justification</label>
                <textarea value={justification} onChange={e => setJustification(e.target.value)} rows={3} placeholder="Why do you need more time?"
                  className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-600 focus:outline-none focus:border-cyan-500/50" />
              </div>
              <div className="flex gap-3">
                <button onClick={handleExtend} disabled={loading || justification.length < 10}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold disabled:opacity-40 transition-all">
                  {loading ? "Extending..." : "Extend"}
                </button>
                <button onClick={() => { setShowExtend(false); setJustification(""); setError(null) }}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all">
                  Cancel
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Release Confirmation Modal */}
      <AnimatePresence>
        {showRelease && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0d1117] border border-white/10 rounded-2xl p-6 max-w-md w-full">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-red-500/20">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Release this issue?</h3>
                  <p className="text-[11px] text-gray-500">This action cannot be undone</p>
                </div>
              </div>
              <p className="text-sm text-gray-400 mb-5 leading-relaxed">
                You will lose your claim on this issue and it will become available for others to pick up. Any progress you've made won't be lost — you can always submit a PR independently.
              </p>
              <div className="mb-5">
                <label className="block text-xs font-medium text-gray-400 mb-1.5">Reason for releasing</label>
                <select value={releaseReason} onChange={e => setReleaseReason(e.target.value)}
                  className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm focus:outline-none focus:border-cyan-500/50 appearance-none cursor-pointer">
                  <option value="" className="bg-[#0d1117]">Select a reason...</option>
                  <option value="no_longer_available" className="bg-[#0d1117]">No longer have time to work on it</option>
                  <option value="too_difficult" className="bg-[#0d1117]">Issue is too difficult for me</option>
                  <option value="issue_closed" className="bg-[#0d1117]">Issue was closed on GitHub</option>
                  <option value="resolved_by_others" className="bg-[#0d1117]">Issue was resolved by someone else</option>
                  <option value="unclear_requirements" className="bg-[#0d1117]">Requirements are unclear or incomplete</option>
                  <option value="blocked" className="bg-[#0d1117]">Blocked by external dependency</option>
                  <option value="other" className="bg-[#0d1117]">Other</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button onClick={handleRelease} disabled={loading || !releaseReason}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-red-500 to-amber-600 text-white text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all">
                  <Undo2 className="h-4 w-4" /> {loading ? "Releasing..." : "Yes, Release"}
                </button>
                <button onClick={() => { setShowRelease(false); setReleaseReason("") }}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all">
                  Keep Working
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Submit PR Modal */}
      <AnimatePresence>
        {showSubmitPR && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0d1117] border border-white/10 rounded-2xl p-6 max-w-lg w-full">

              {/* Success state */}
              {prSubmitted ? (
                <div className="text-center py-4">
                  <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 mb-4">
                    <CheckCircle2 className="h-7 w-7 text-emerald-400" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-1">PR Submitted</h3>
                  <p className="text-sm text-gray-400 mb-1">
                    Pull request #{prResult?.pr_number} has been recorded.
                  </p>
                  {prResult?.points_earned ? (
                    <p className="text-sm text-cyan-400 font-medium">+{prResult.points_earned} points earned</p>
                  ) : null}
                  {prResult?.achievements && prResult.achievements.length > 0 && (
                    <div className="mt-3 space-y-1">
                      <p className="text-xs text-gray-500">New achievements unlocked:</p>
                      {prResult.achievements.map(a => (
                        <span key={a} className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/20 mr-1">
                          🏆 {a}
                        </span>
                      ))}
                    </div>
                  )}
                  <button onClick={() => { setShowSubmitPR(false); setPrSubmitted(false); setPrUrl(""); setPrResult(null) }}
                    className="mt-5 px-6 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all">
                    Close
                  </button>
                </div>
              ) : (
                <>
                  <div className="flex items-center gap-3 mb-5">
                    <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20">
                      <GitPullRequest className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">Submit Pull Request</h3>
                      <p className="text-[11px] text-gray-500">Link your PR to this issue</p>
                    </div>
                  </div>

                  {error && (
                    <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
                    </div>
                  )}

                  <div className="mb-4">
                    <label className="block text-xs font-medium text-gray-400 mb-1.5">Pull Request URL</label>
                    <input type="url" value={prUrl} onChange={e => setPrUrl(e.target.value)}
                      placeholder="https://github.com/owner/repo/pull/123"
                      className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-600 focus:outline-none focus:border-cyan-500/50" />
                  </div>

                  <div className="mb-5 p-3 rounded-xl bg-amber-500/5 border border-amber-500/10">
                    <div className="flex items-start gap-2">
                      <Info className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />
                      <div className="text-[12px] text-gray-400 leading-relaxed space-y-1">
                        <p>The PR must be created from your GitHub account. Submitting someone else's PR will not earn you any rewards.</p>
                        <p>Your PR will be validated against the GitHub API to confirm authorship and link to this issue.</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button onClick={handleSubmitPR} disabled={loading || !prUrl.trim()}
                      className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-600 text-white text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all">
                      <GitPullRequest className="h-4 w-4" /> {loading ? "Validating..." : "Submit PR"}
                    </button>
                    <button onClick={() => { setShowSubmitPR(false); setPrUrl(""); setError(null) }}
                      className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all">
                      Cancel
                    </button>
                  </div>

                  {/* Dev-only simulate buttons */}
                  {process.env.NODE_ENV === "development" && (
                    <div className="mt-4 pt-4 border-t border-white/5">
                      <p className="text-[11px] text-gray-600 mb-2">Dev only — simulate without GitHub</p>
                      <div className="flex gap-2">
                        <button onClick={() => handleSimulatePR(true)} disabled={loading}
                          className="flex-1 px-3 py-2 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-medium hover:bg-purple-500/20 disabled:opacity-40 transition-all">
                          {loading ? "Simulating..." : "Simulate Merged PR"}
                        </button>
                        <button onClick={() => handleSimulatePR(false)} disabled={loading}
                          className="flex-1 px-3 py-2 rounded-lg bg-gray-500/10 border border-gray-500/20 text-gray-400 text-xs font-medium hover:bg-gray-500/20 disabled:opacity-40 transition-all">
                          {loading ? "Simulating..." : "Simulate Open PR"}
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Service Agreement Modal */}
      <AnimatePresence>
        {showAgreement && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0d1117] border border-white/10 rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center gap-3 mb-5">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20">
                  <ShieldCheck className="h-5 w-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Contribution Agreement</h3>
                  <p className="text-[11px] text-gray-500">Please review before you start working</p>
                </div>
              </div>

              <div className="space-y-3 mb-6 text-sm text-gray-300 leading-relaxed">
                <div className="bg-white/[0.03] rounded-xl p-4 border border-white/5 space-y-3">
                  <p>By claiming this issue, you agree to the following:</p>
                  <ul className="space-y-2 text-gray-400">
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span>You will submit a pull request within the claim deadline shown on the issue page. If you need more time, use the Extend option before it expires.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span>All code you submit must be your own original work. Using AI tools for assistance is fine, but copy-pasting entire solutions is not.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span>You will follow the repository's contributing guidelines, code style, and review process.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span>Be respectful in all interactions with maintainers and other contributors.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                      <span>If you can no longer work on this issue, release it promptly so others can pick it up.</span>
                    </li>
                  </ul>
                </div>
              </div>

              <label className="flex items-start gap-3 mb-5 cursor-pointer group">
                <input type="checkbox" checked={agreedTerms} onChange={e => setAgreedTerms(e.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 text-cyan-500 focus:ring-cyan-500/30 accent-cyan-500" />
                <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                  I have read and agree to the contribution guidelines above
                </span>
              </label>

              <div className="flex gap-3">
                <button onClick={handleAcceptAgreement} disabled={!agreedTerms}
                  className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-600 text-white text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all">
                  <ExternalLink className="h-4 w-4" /> Start Working on GitHub
                </button>
                <button onClick={() => { setShowAgreement(false); setAgreedTerms(false) }}
                  className="px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm font-medium hover:bg-white/10 transition-all">
                  Later
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
