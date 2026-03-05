import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, Users, MessageCircle, GitPullRequest, Award, Globe, Handshake } from "lucide-react"

export const metadata = { title: "Community — Contributors.in" }

export default function CommunityPage() {
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
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-pink-500/20 to-purple-500/20 mb-6">
            <Users className="h-10 w-10 text-pink-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">Community</h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Join a global network of developers who believe in the power of open source collaboration.
          </p>
        </div>

        <div className="space-y-6">
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500/20 to-purple-500/20">
                <Handshake className="h-5 w-5 text-pink-400" />
              </div>
              <h2 className="text-xl font-bold text-white">A Place for Everyone</h2>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Whether you&apos;re a student writing your first line of code or a senior engineer looking to give back, our community welcomes you. We believe that diverse perspectives make better software, and every contribution — no matter how small — moves the ecosystem forward.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { icon: MessageCircle, title: "Peer Support", desc: "Get help from fellow contributors who've been in your shoes. Ask questions, share learnings, and grow together." },
              { icon: GitPullRequest, title: "Collaborative Learning", desc: "Learn by doing. Review others' PRs, pair on issues, and build real-world skills through hands-on collaboration." },
              { icon: Award, title: "Recognition", desc: "Your contributions are celebrated. Earn achievements, get featured on leaderboards, and build a portfolio that stands out." },
              { icon: Globe, title: "Global Reach", desc: "Connect with developers from around the world. Open source knows no borders, and neither does our community." },
            ].map((item) => (
              <div key={item.title} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
                <item.icon className="h-6 w-6 text-cyan-400 mb-3" />
                <h3 className="text-base font-bold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

          <div className="bg-gradient-to-br from-cyan-500/[0.06] to-blue-500/[0.03] backdrop-blur-sm border border-cyan-500/15 rounded-2xl p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-3">Ready to Join?</h2>
            <p className="text-gray-400 mb-6 max-w-lg mx-auto">
              Sign in with GitHub and start your open source journey today. The community is waiting for you.
            </p>
            <Link href="/auth/signin" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all">
              Get Started
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
