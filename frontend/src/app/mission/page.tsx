import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, Target, Shield, Zap, Users, Heart } from "lucide-react"

export const metadata = { title: "Our Mission — Contributors.in" }

export default function MissionPage() {
  return (
    <div className="min-h-screen bg-black relative">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

      <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
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
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 mb-6">
            <Target className="h-10 w-10 text-emerald-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">Our Mission</h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            To lower the barrier to open source contribution and empower every developer to make an impact.
          </p>
        </div>

        <div className="space-y-6">
          {[
            {
              icon: Zap,
              title: "Remove Friction",
              text: "We eliminate the guesswork from open source. Our AI matches you with issues that fit your skills, our platform handles the logistics, and our guides walk you through every step — so you can focus on what matters: writing great code.",
            },
            {
              icon: Users,
              title: "Build an Inclusive Community",
              text: "Open source should reflect the diversity of the developer community. We actively work to create a welcoming space for developers of all backgrounds, experience levels, and geographies. Every voice matters, every contribution counts.",
            },
            {
              icon: Shield,
              title: "Promote Quality Contributions",
              text: "We don't just count PRs — we encourage meaningful contributions. Our achievement system rewards quality over quantity, and our AI guidance helps contributors understand the codebase before they write a single line.",
            },
            {
              icon: Heart,
              title: "Support Maintainers",
              text: "Open source maintainers carry an enormous burden. By directing well-prepared contributors to their projects and ensuring quality submissions, we help reduce maintainer fatigue and keep the open source ecosystem healthy.",
            },
          ].map((item) => (
            <div key={item.title} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20">
                  <item.icon className="h-5 w-5 text-emerald-400" />
                </div>
                <h2 className="text-xl font-bold text-white">{item.title}</h2>
              </div>
              <p className="text-gray-400 leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
