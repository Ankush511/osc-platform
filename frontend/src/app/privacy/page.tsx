import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, Shield } from "lucide-react"

export const metadata = { title: "Privacy Policy — Contributors.in" }

export default function PrivacyPage() {
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
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 mb-6">
            <Shield className="h-8 w-8 text-cyan-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-3">Privacy Policy</h1>
          <p className="text-gray-500 text-sm">Last updated: March 1, 2026</p>
        </div>

        <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12 space-y-10 text-gray-400 leading-relaxed">

          <section>
            <h2 className="text-xl font-bold text-white mb-4">1. Introduction</h2>
            <p className="mb-3">
              Contributors.in (&quot;we,&quot; &quot;our,&quot; or &quot;the Platform&quot;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our open source contribution platform.
            </p>
            <p>
              By accessing or using Contributors.in, you agree to the terms of this Privacy Policy. If you do not agree with the practices described herein, please do not use the Platform.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">2. Information We Collect</h2>
            <h3 className="text-base font-semibold text-gray-300 mb-2">2.1 Information from GitHub OAuth*</h3>
            <p className="mb-3">
              When you sign in using GitHub OAuth, we receive and store the following information from your GitHub profile:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4 mb-4">
              <li>GitHub username and unique GitHub ID</li>
              <li>Email address (if publicly available on your GitHub profile)</li>
              <li>Profile avatar URL</li>
              <li>Display name, bio, and location (if provided)</li>
            </ul>
            <h3 className="text-base font-semibold text-gray-300 mb-2">2.2 Platform Activity Data*</h3>
            <p className="mb-3">We collect data about your activity on the Platform, including:</p>
            <ul className="list-disc list-inside space-y-1 ml-4 mb-4">
              <li>Issues you browse, claim, and contribute to</li>
              <li>Pull request URLs you submit</li>
              <li>Achievement progress and points earned</li>
              <li>Preferred programming languages and labels</li>
              <li>Timestamps of actions performed on the Platform</li>
            </ul>
            <h3 className="text-base font-semibold text-gray-300 mb-2">2.3 Technical Data*</h3>
            <p>We automatically collect certain technical information when you access the Platform, including IP address, browser type, device information, and access timestamps. This data is used for security, rate limiting, and service improvement purposes.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">3. How We Use Your Information</h2>
            <p className="mb-3">We use the information we collect for the following purposes:*</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>To authenticate your identity and manage your account</li>
              <li>To match you with relevant open source issues using our AI recommendation engine</li>
              <li>To track your contributions, achievements, and platform statistics</li>
              <li>To display your profile information on leaderboards and public profiles</li>
              <li>To communicate with you about your account and platform updates</li>
              <li>To enforce our Terms of Service and prevent abuse</li>
              <li>To improve the Platform through analytics and usage patterns</li>
              <li>To provide AI-powered issue explanations and solution suggestions</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">4. AI and Data Processing*</h2>
            <p className="mb-3">
              Our Platform uses AI services (powered by AWS Bedrock) to provide issue analysis, difficulty assessment, and contribution guidance. When you request an AI-generated explanation:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>The issue title, description, and metadata are sent to the AI service for processing</li>
              <li>Your personal information is not included in AI prompts</li>
              <li>AI-generated responses are cached to improve performance and reduce redundant processing</li>
              <li>We do not use your contribution data to train AI models</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">5. Data Sharing and Disclosure*</h2>
            <p className="mb-3">We do not sell your personal information. We may share your information in the following circumstances:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Public profile information (username, avatar, contribution stats) is visible to other Platform users</li>
              <li>With GitHub&apos;s API when verifying pull requests and syncing issue data</li>
              <li>With cloud infrastructure providers (AWS) for hosting and AI processing</li>
              <li>When required by law, regulation, or legal process</li>
              <li>To protect the rights, safety, and security of our users and the Platform</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">6. Data Retention*</h2>
            <p className="mb-3">
              We retain your personal information for as long as your account is active or as needed to provide you with our services. Specifically:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Account data is retained until you request deletion</li>
              <li>Contribution records are retained to maintain platform integrity and leaderboard accuracy</li>
              <li>Technical logs (IP addresses, access logs) are retained for up to 90 days</li>
              <li>Cached AI explanations are retained for up to 24 hours</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">7. Your Rights (GDPR Compliance)*</h2>
            <p className="mb-3">If you are located in the European Economic Area, you have the following rights:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Right to access your personal data</li>
              <li>Right to rectification of inaccurate data</li>
              <li>Right to erasure (&quot;right to be forgotten&quot;)</li>
              <li>Right to restrict processing</li>
              <li>Right to data portability</li>
              <li>Right to object to processing</li>
            </ul>
            <p className="mt-3">
              You can exercise these rights through the Settings page on the Platform, which includes data export and account deletion functionality.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">8. Security*</h2>
            <p>
              We implement industry-standard security measures to protect your data, including HTTPS encryption, JWT-based authentication, rate limiting, DDoS protection, security headers (CSP, HSTS), and regular security audits. However, no method of transmission over the Internet is 100% secure, and we cannot guarantee absolute security.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">9. Cookies and Local Storage*</h2>
            <p>
              We use session cookies to maintain your authentication state. We do not use third-party tracking cookies or advertising cookies. Session data is stored securely using NextAuth.js with JWT-based sessions that expire after 7 days of inactivity.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">10. Children&apos;s Privacy*</h2>
            <p>
              The Platform is not intended for children under the age of 13. We do not knowingly collect personal information from children under 13. If we become aware that we have collected data from a child under 13, we will take steps to delete that information promptly.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">11. Changes to This Policy*</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the updated policy on this page and updating the &quot;Last updated&quot; date. Your continued use of the Platform after changes are posted constitutes your acceptance of the revised policy.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">12. Contact Us*</h2>
            <p>
              If you have any questions about this Privacy Policy or our data practices, please contact us through our GitHub repository or by reaching out to the platform administrators through the Settings page.*
            </p>
          </section>

          <div className="pt-6 border-t border-white/5 text-xs text-gray-600">
            <p>* Sections marked with an asterisk contain legally binding terms. Please read them carefully.</p>
          </div>
        </div>
      </main>
    </div>
  )
}
