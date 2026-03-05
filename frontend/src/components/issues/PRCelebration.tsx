"use client"

import { useEffect, useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  Trophy, Star, Sparkles, Award, X, Target, Flame, Zap,
  Crown, Rocket, Globe, Code, Heart, Shield, Medal,
} from "lucide-react"

// Achievement icon/color mapping
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
const DEFAULT_STYLE = { icon: Award, gradient: "from-amber-500 to-orange-500" }

interface Props {
  show: boolean
  pointsEarned: number
  prNumber?: number
  achievements?: string[]
  onClose: () => void
}

function Confetti() {
  const particles = useMemo(() =>
    Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      delay: Math.random() * 0.8,
      duration: 1.5 + Math.random() * 2,
      size: 4 + Math.random() * 6,
      color: ["bg-cyan-400","bg-blue-400","bg-purple-400","bg-amber-400","bg-emerald-400","bg-pink-400"][Math.floor(Math.random() * 6)],
      rotation: Math.random() * 360,
    })), [])

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map(p => (
        <motion.div key={p.id} className={`absolute rounded-sm ${p.color}`}
          style={{ left: `${p.x}%`, width: p.size, height: p.size, rotate: p.rotation }}
          initial={{ top: "-5%", opacity: 1 }}
          animate={{ top: "110%", opacity: 0, rotate: p.rotation + 360 }}
          transition={{ duration: p.duration, delay: p.delay, ease: "easeIn" }}
        />
      ))}
    </div>
  )
}

function AnimatedScore({ value }: { value: number }) {
  const [display, setDisplay] = useState(0)
  useEffect(() => {
    if (value === 0) return
    const steps = 30
    const inc = value / steps
    let cur = 0
    const t = setInterval(() => {
      cur += inc
      if (cur >= value) { setDisplay(value); clearInterval(t) }
      else setDisplay(Math.floor(cur))
    }, 40)
    return () => clearInterval(t)
  }, [value])
  return <span>{display}</span>
}

export default function PRCelebration({ show, pointsEarned, prNumber, achievements = [], onClose }: Props) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <Confetti />

          <motion.div
            initial={{ scale: 0.7, opacity: 0, y: 30 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", damping: 20, stiffness: 250 }}
            className="relative bg-gradient-to-b from-[#111827] to-[#0d1117] border border-white/10 rounded-3xl p-8 max-w-md w-full text-center overflow-hidden"
          >
            {/* Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-gradient-to-b from-amber-500/20 via-amber-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

            <button onClick={onClose} className="absolute top-4 right-4 text-gray-600 hover:text-gray-400 transition-colors z-10">
              <X className="h-5 w-5" />
            </button>

            {/* Trophy */}
            <motion.div initial={{ scale: 0, rotate: -20 }} animate={{ scale: 1, rotate: 0 }}
              transition={{ type: "spring", damping: 12, stiffness: 200, delay: 0.2 }}
              className="relative mx-auto mb-6">
              <div className="relative inline-flex items-center justify-center w-24 h-24">
                <motion.div className="absolute inset-0 rounded-full border-2 border-amber-400/30"
                  animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }} />
                <motion.div className="absolute inset-0 rounded-full border-2 border-amber-400/20"
                  animate={{ scale: [1, 1.7, 1], opacity: [0.3, 0, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.3 }} />
                <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-amber-400 via-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-500/30">
                  <Trophy className="h-10 w-10 text-white drop-shadow-lg" />
                </div>
              </div>
            </motion.div>

            {/* Title */}
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <h2 className="text-2xl font-black text-white mb-1">Contribution Recorded</h2>
              {prNumber && <p className="text-sm text-gray-500">Pull Request #{prNumber}</p>}
            </motion.div>

            {/* Points */}
            <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, type: "spring", damping: 15 }}
              className="mt-6 mb-6">
              <div className="inline-flex items-center gap-3 px-6 py-4 rounded-2xl bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-purple-500/10 border border-cyan-500/20">
                <Star className="h-6 w-6 text-cyan-400" />
                <div className="text-left">
                  <p className="text-[11px] text-gray-500 uppercase tracking-wider font-medium">Points Earned</p>
                  <p className="text-3xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                    +<AnimatedScore value={pointsEarned} />
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Achievements */}
            {achievements.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }} className="mb-6">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Sparkles className="h-4 w-4 text-amber-400" />
                  <p className="text-xs font-semibold text-amber-300 uppercase tracking-wider">Achievements Unlocked</p>
                  <Sparkles className="h-4 w-4 text-amber-400" />
                </div>
                <div className="flex flex-col gap-2">
                  {achievements.map((name, i) => {
                    const style = ACHIEVEMENT_STYLES[name] || DEFAULT_STYLE
                    const Icon = style.icon
                    return (
                      <motion.div key={name}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1 + i * 0.15, type: "spring", damping: 14 }}
                        className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/10">
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${style.gradient} flex items-center justify-center shrink-0 shadow-lg`}>
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-bold text-white">{name}</p>
                          <p className="text-[11px] text-gray-500">Achievement unlocked</p>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </motion.div>
            )}

            {/* CTA */}
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              transition={{ delay: achievements.length > 0 ? 1.3 : 0.9 }}>
              <button onClick={onClose}
                className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/20">
                Continue
              </button>
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
