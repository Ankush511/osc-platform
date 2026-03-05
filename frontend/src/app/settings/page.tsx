import { auth, signOut } from "@/auth"
import { redirect } from "next/navigation"
import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, LogOut, User, Bell, Shield } from "lucide-react"

export default async function SettingsPage() {
  const session = await auth()

  if (!session?.user || !session.accessToken) {
    redirect("/auth/signin")
  }

  return (
    <div className="min-h-screen bg-black relative">
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)]" />
      </div>

      <nav className="sticky top-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-2xl">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors">
              <ArrowLeft className="h-4 w-4" />
              Dashboard
            </Link>
            <Link href="/" className="flex items-center space-x-2">
              <LogoIcon size="sm" />
              <span className="text-sm font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Contributors.in</span>
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-black text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account and preferences</p>
        </div>

        <div className="space-y-6">
          {/* Account */}
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <User className="h-5 w-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-white">Account</h2>
            </div>
            <div className="flex items-center gap-4">
              <img
                src={session.user.image || ""}
                alt={session.user.name || ""}
                className="h-12 w-12 rounded-full ring-2 ring-cyan-500/30"
              />
              <div>
                <p className="text-white font-medium">{session.user.name}</p>
                <p className="text-gray-400 text-sm">{session.user.email}</p>
              </div>
            </div>
          </div>

          {/* Notifications placeholder */}
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <Bell className="h-5 w-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-white">Notifications</h2>
            </div>
            <p className="text-gray-400 text-sm">Email notifications for claim expirations and PR updates coming soon.</p>
          </div>

          {/* Privacy */}
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-5 w-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-white">Privacy</h2>
            </div>
            <p className="text-gray-400 text-sm mb-4">We only access your public GitHub profile. No private repos are read.</p>
          </div>

          {/* Sign out */}
          <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-red-500/10 rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <LogOut className="h-5 w-5 text-red-400" />
                <div>
                  <h2 className="text-lg font-bold text-white">Sign Out</h2>
                  <p className="text-gray-400 text-sm">Sign out of your account</p>
                </div>
              </div>
              <form action={async () => { "use server"; await signOut({ redirectTo: "/" }) }}>
                <button type="submit" className="px-5 py-2.5 rounded-xl border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-500/10 transition-all">
                  Sign Out
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
