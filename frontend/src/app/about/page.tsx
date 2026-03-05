import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, Users, Heart, Globe, Code2, Sparkles } from "lucide-react"

export const metadata = { title: "About Us — Contributors.in" }

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-black relative">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

      <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                <LogoIcon size="md" />
              </div>
              <div>
                <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Contributors</span>
                <span className="text-cyan-400 text-xs font-mono">.in</span>
              </div>
            </Link>
            <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
              <ArrowLeft className="h-4 w-4" /> Home
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 lg:px-8 py-16">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">About Us</h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            We&apos;re a team of developers passionate about making open source accessible to everyone.
          </p>
        </div>

        <div className="space-y-8">
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20">
                <Heart className="h-5 w-5 text-cyan-400" />
              </div>
              <h2 className="text-xl font-bold text-white">Our Story</h2>
            </div>
            <p className="text-gray-400 leading-relaxed mb-4">
              Contributors.in was born from a simple observation: too many talented developers want to contribute to open source but don&apos;t know where to start. The barrier to entry felt unnecessarily high — finding the right project, understanding codebases, and navigating community norms can be overwhelming.
            </p>
            <p className="text-gray-400 leading-relaxed">
              We built this platform to bridge that gap. By combining AI-powered issue matching, gamification, and a supportive community, we&apos;ve created a space where anyone — from first-time contributors to seasoned developers — can find meaningful ways to give back to the open source ecosystem.
            </p>
          </div>

          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20">
                <Sparkles className="h-5 w-5 text-purple-400" />
              </div>
              <h2 className="text-xl font-bold text-white">What We Do</h2>
            </div>
            <p className="text-gray-400 leading-relaxed">
              We curate beginner-friendly issues from hundreds of open source projects, use AI to match them to your skill level, and provide guidance every step of the way. Our achievement system keeps you motivated, and our community ensures you never feel alone on your open source journey.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: Users, label: "1,000+", desc: "Active developers", color: "cyan" },
              { icon: Globe, label: "300+", desc: "Open source projects", color: "blue" },
              { icon: Code2, label: "500+", desc: "Issues resolved", color: "purple" },
            ].map((s) => (
              <div key={s.label} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center">
                <s.icon className={`h-8 w-8 text-${s.color}-400 mx-auto mb-3`} />
                <div className="text-2xl font-black text-white mb-1">{s.label}</div>
                <div className="text-gray-500 text-sm">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
