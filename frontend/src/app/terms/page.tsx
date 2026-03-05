import Link from "next/link"
import { LogoIcon } from "@/components/ui/Logo"
import { ArrowLeft, FileText } from "lucide-react"

export const metadata = { title: "Terms & Conditions — Contributors.in" }

export default function TermsPage() {
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
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 mb-6">
            <FileText className="h-8 w-8 text-purple-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white mb-3">Terms &amp; Conditions</h1>
          <p className="text-gray-500 text-sm">Last updated: March 1, 2026</p>
        </div>

        <div className="bg-gradient-to-br from-white/[0.07] to-white/[0.02] backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12 space-y-10 text-gray-400 leading-relaxed">

          <section>
            <h2 className="text-xl font-bold text-white mb-4">1. Acceptance of Terms*</h2>
            <p className="mb-3">
              By accessing or using Contributors.in (&quot;the Platform&quot;), you agree to be bound by these Terms and Conditions (&quot;Terms&quot;). If you do not agree to these Terms, you must not use the Platform. These Terms constitute a legally binding agreement between you and Contributors.in.
            </p>
            <p>
              We reserve the right to modify these Terms at any time. Continued use of the Platform after modifications constitutes acceptance of the updated Terms.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">2. Eligibility*</h2>
            <p className="mb-3">To use the Platform, you must:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Be at least 13 years of age</li>
              <li>Have a valid GitHub account in good standing</li>
              <li>Agree to comply with these Terms and all applicable laws</li>
              <li>Not have been previously banned or removed from the Platform</li>
            </ul>
            <p className="mt-3">If you are under 18, you represent that you have your parent or guardian&apos;s consent to use the Platform.*</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">3. Account and Authentication*</h2>
            <p className="mb-3">
              The Platform uses GitHub OAuth for authentication. By signing in, you authorize us to access your GitHub profile information as described in our Privacy Policy. You are responsible for:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Maintaining the security of your GitHub account</li>
              <li>All activities that occur under your account on the Platform</li>
              <li>Notifying us immediately of any unauthorized use of your account</li>
              <li>Ensuring your GitHub profile information is accurate and up to date</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">4. Acceptable Use*</h2>
            <p className="mb-3">When using the Platform, you agree to:</p>
            <ul className="list-disc list-inside space-y-1 ml-4 mb-4">
              <li>Submit only your own original work in pull requests</li>
              <li>Follow the contributing guidelines of each repository you contribute to</li>
              <li>Be respectful and professional in all interactions with maintainers and other contributors</li>
              <li>Release claimed issues promptly if you can no longer work on them</li>
              <li>Not claim issues with no intention of completing them</li>
              <li>Not manipulate the achievement or points system through fraudulent activity</li>
            </ul>
            <p className="mb-3">You must not:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Use the Platform for any unlawful purpose</li>
              <li>Attempt to gain unauthorized access to the Platform or its systems</li>
              <li>Interfere with or disrupt the Platform&apos;s infrastructure</li>
              <li>Scrape, crawl, or use automated tools to access the Platform without permission</li>
              <li>Impersonate another user or misrepresent your identity</li>
              <li>Submit malicious code, spam, or harmful content through pull requests</li>
              <li>Circumvent rate limits, security measures, or access controls*</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">5. Issue Claiming and Contributions*</h2>
            <p className="mb-3">The Platform provides a system for claiming and contributing to open source issues. By using this system:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Claiming an issue creates a time-limited reservation. You must submit a pull request within the claim deadline or the issue will be automatically released.</li>
              <li>Claim deadlines vary by difficulty: Easy (7 days), Medium (14 days), Hard (21 days). Extensions may be requested with justification.*</li>
              <li>Submitting a pull request does not guarantee it will be merged. Merge decisions are made by the repository maintainers, not by Contributors.in.</li>
              <li>Points and achievements are awarded based on Platform activity and are subject to our anti-fraud policies.</li>
              <li>We reserve the right to revoke points or achievements earned through fraudulent or abusive behavior.*</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">6. AI-Powered Features*</h2>
            <p className="mb-3">The Platform provides AI-generated content including issue explanations, difficulty assessments, and solution suggestions. Regarding these features:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>AI-generated content is provided for informational and educational purposes only</li>
              <li>We do not guarantee the accuracy, completeness, or suitability of AI-generated content</li>
              <li>You should not rely solely on AI suggestions when making contributions</li>
              <li>AI-generated code suggestions should be reviewed and understood before submission</li>
              <li>We are not responsible for any consequences arising from the use of AI-generated content*</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">7. Intellectual Property*</h2>
            <p className="mb-3">
              The Platform&apos;s design, code, branding, and content (excluding user-generated content and open source project data) are the intellectual property of Contributors.in. You may not reproduce, distribute, or create derivative works without our express written permission.
            </p>
            <p>
              Code you contribute to open source projects through the Platform is subject to the license of the respective repository. Contributors.in does not claim any ownership over your contributions.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">8. Limitation of Liability*</h2>
            <p className="mb-3">
              To the maximum extent permitted by applicable law, Contributors.in and its operators shall not be liable for:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Any indirect, incidental, special, consequential, or punitive damages</li>
              <li>Loss of profits, data, or business opportunities</li>
              <li>Damages arising from your use of or inability to use the Platform</li>
              <li>Actions taken by repository maintainers regarding your pull requests</li>
              <li>Inaccuracies in AI-generated content or recommendations</li>
              <li>Unauthorized access to your account due to your failure to maintain security</li>
            </ul>
            <p className="mt-3">The Platform is provided &quot;as is&quot; and &quot;as available&quot; without warranties of any kind, either express or implied.*</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">9. Termination*</h2>
            <p className="mb-3">
              We reserve the right to suspend or terminate your access to the Platform at any time, with or without cause, and with or without notice. Grounds for termination include but are not limited to:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Violation of these Terms</li>
              <li>Fraudulent or abusive behavior</li>
              <li>Harassment of other users or maintainers</li>
              <li>Submission of malicious code</li>
              <li>Repeated claiming and abandoning of issues</li>
            </ul>
            <p className="mt-3">Upon termination, your right to use the Platform ceases immediately. Provisions that by their nature should survive termination shall survive.*</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">10. Indemnification*</h2>
            <p>
              You agree to indemnify, defend, and hold harmless Contributors.in and its operators from and against any claims, liabilities, damages, losses, and expenses (including reasonable legal fees) arising out of or in any way connected with your access to or use of the Platform, your violation of these Terms, or your infringement of any third-party rights.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">11. Governing Law*</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of India, without regard to its conflict of law provisions. Any disputes arising under these Terms shall be subject to the exclusive jurisdiction of the courts located in India.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">12. Severability*</h2>
            <p>
              If any provision of these Terms is found to be unenforceable or invalid, that provision shall be limited or eliminated to the minimum extent necessary so that these Terms shall otherwise remain in full force and effect.*
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-white mb-4">13. Contact*</h2>
            <p>
              For questions about these Terms, please contact us through our GitHub repository or through the Platform&apos;s Settings page. We will make reasonable efforts to respond to inquiries within a timely manner.*
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
