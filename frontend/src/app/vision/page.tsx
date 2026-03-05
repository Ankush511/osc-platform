import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, Eye, Lightbulb, Globe, Rocket } from "lucide-react"

export const metadata = { title: "Our Vision — Contributors.in" }

export default function VisionPage() {
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
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 mb-6">
            <Eye className="h-10 w-10 text-blue-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4">Our Vision</h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            A world where every developer, regardless of experience, can contribute meaningfully to open source software.
          </p>
        </div>

        <div className="space-y-6">
          {[
            {
              icon: Globe,
              title: "Democratize Open Source",
              text: "We envision a future where contributing to open source is as natural as writing code. No gatekeeping, no intimidation — just a welcoming ecosystem where every pull request matters and every contributor is valued.",
            },
            {
              icon: Lightbulb,
              title: "AI-Powered Developer Growth",
              text: "We see AI not as a replacement for developers, but as a mentor. Our vision is to use artificial intelligence to guide developers toward the right challenges at the right time, accelerating their growth while ensuring they build real skills.",
            },
            {
              icon: Rocket,
              title: "Bridge Education and Industry",
              text: "We believe open source contributions should be a recognized pathway into the tech industry. Our vision is to create a platform where students and self-taught developers can build verifiable portfolios that speak louder than any resume.",
            },
          ].map((item) => (
            <div key={item.title} className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20">
                  <item.icon className="h-5 w-5 text-blue-400" />
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
