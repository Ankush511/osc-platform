"use client"

interface LogoIconProps {
  size?: "sm" | "md" | "lg"
}

const SIZES = {
  sm: { container: 36, radius: 10, svg: 24, svgView: "0 0 120 140" },
  md: { container: 44, radius: 13, svg: 30, svgView: "0 0 120 140" },
  lg: { container: 56, radius: 16, svg: 38, svgView: "0 0 120 140" },
}

export function LogoIcon({ size = "md" }: LogoIconProps) {
  const s = SIZES[size]
  return (
    <div
      style={{
        width: s.container,
        height: s.container,
        borderRadius: s.radius,
        background: "linear-gradient(150deg, #04102e 0%, #0b1e72 45%, #1348c4 80%, #1a55e5 100%)",
        boxShadow:
          "0 0 0 1.5px rgba(90,140,255,0.18), 0 8px 32px rgba(18,72,220,0.4), inset 0 1px 0 rgba(255,255,255,0.1)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative" as const,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute" as const,
          inset: 0,
          borderRadius: s.radius,
          background: "radial-gradient(ellipse at 42% 28%, rgba(120,170,255,0.12) 0%, transparent 65%)",
        }}
      />
      <svg width={s.svg} height={s.svg * 1.135} viewBox={s.svgView} fill="none">
        <defs>
          <linearGradient id="tl" x1="0.5" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#bae6fd" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
          <linearGradient id="tr" x1="0.5" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#bae6fd" />
            <stop offset="100%" stopColor="#a78bfa" />
          </linearGradient>
          <linearGradient id="bl" x1="0" y1="0" x2="0.5" y2="1">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#38bdf8" />
          </linearGradient>
          <linearGradient id="br" x1="1" y1="0" x2="0.5" y2="1">
            <stop offset="0%" stopColor="#a78bfa" />
            <stop offset="100%" stopColor="#38bdf8" />
          </linearGradient>
          <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="3.5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="nodeglow" x="-150%" y="-150%" width="400%" height="400%">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d="M60 14 C60 44, 26 44, 26 74" stroke="url(#tl)" strokeWidth="8" strokeLinecap="round" fill="none" filter="url(#glow)" />
        <path d="M60 14 C60 44, 94 44, 94 74" stroke="url(#tr)" strokeWidth="8" strokeLinecap="round" fill="none" filter="url(#glow)" />
        <path d="M26 74 C26 104, 60 104, 60 126" stroke="url(#bl)" strokeWidth="8" strokeLinecap="round" fill="none" filter="url(#glow)" />
        <path d="M94 74 C94 104, 60 104, 60 126" stroke="url(#br)" strokeWidth="8" strokeLinecap="round" fill="none" filter="url(#glow)" />
        <circle cx="60" cy="14" r="12" fill="#93c5fd" filter="url(#nodeglow)" />
        <circle cx="60" cy="14" r="6.5" fill="white" />
        <circle cx="26" cy="74" r="10" fill="#6366f1" filter="url(#nodeglow)" />
        <circle cx="26" cy="74" r="5.5" fill="white" />
        <circle cx="94" cy="74" r="10" fill="#a78bfa" filter="url(#nodeglow)" />
        <circle cx="94" cy="74" r="5.5" fill="white" />
        <circle cx="60" cy="126" r="12" fill="#38bdf8" filter="url(#nodeglow)" />
        <circle cx="60" cy="126" r="6.5" fill="white" />
      </svg>
    </div>
  )
}

export function LogoWithGlow({ size = "md" }: LogoIconProps) {
  return (
    <div className="relative">
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
      <LogoIcon size={size} />
    </div>
  )
}
