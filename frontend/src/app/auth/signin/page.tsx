import { signIn } from "@/auth"
import Link from "next/link"
import { LogoWithGlow } from "@/components/ui/Logo"
import { Github, ArrowRight, Sparkles, Shield, Zap } from "lucide-react"

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-black relative flex items-center justify-center px-4">
      {/* Background grid */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
              <LogoWithGlow size="lg" />
            </div>
            <div>
              <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                Contributors
              </span>
              <span className="text-cyan-400 text-xs font-mono">.in</span>
            </div>
          </Link>
        </div>

        {/* Card */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-3xl blur-2xl" />
          <div className="relative bg-gradient-to-br from-white/[0.08] to-white/[0.02] backdrop-blur-xl border border-white/10 rounded-3xl p-8 sm:p-10">
            {/* Badge */}
            <div className="flex justify-center mb-6">
              <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/20">
                <Sparkles className="h-4 w-4 text-cyan-400 animate-pulse" />
                <span className="text-xs text-cyan-300 font-medium">Join 4,000+ developers</span>
              </div>
            </div>

            <h1 className="text-3xl font-black text-center text-white mb-2">
              Welcome back
            </h1>
            <p className="text-center text-gray-400 text-sm mb-8">
              Sign in to continue your open source journey
            </p>

            {/* Sign in button */}
            <form
              action={async () => {
                "use server"
                await signIn("github", { redirectTo: "/dashboard" })
              }}
            >
              <button
                type="submit"
                className="group w-full flex items-center justify-center gap-3 px-6 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 text-white font-bold text-base shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300"
              >
                <Github className="h-5 w-5" />
                <span>Continue with GitHub</span>
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </form>

            {/* Features */}
            <div className="mt-8 grid grid-cols-1 gap-3">
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 shrink-0">
                  <Shield className="h-4 w-4 text-cyan-400" />
                </div>
                <span>Secure OAuth — we never see your password</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-400">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-cyan-500/10 shrink-0">
                  <Zap className="h-4 w-4 text-cyan-400" />
                </div>
                <span>Get AI-powered guidance on your first contribution</span>
              </div>
            </div>

            <p className="mt-6 text-[11px] text-center text-gray-600">
              By signing in, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>
        </div>

        {/* Back link */}
        <div className="mt-6 text-center">
          <Link
            href="/"
            className="text-sm text-gray-500 hover:text-cyan-400 transition-colors"
          >
            ← Back to homepage
          </Link>
        </div>
      </div>
    </div>
  )
}
