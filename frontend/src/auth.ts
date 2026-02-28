import NextAuth from "next-auth"
import GitHub from "next-auth/providers/github"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "read:user user:email"
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, account, profile, trigger }) {
      // On initial sign in, exchange GitHub code for backend JWT
      if (account && profile) {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/github/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              code: account.access_token,
              github_id: profile.id,
              username: profile.login,
              email: profile.email,
              avatar_url: profile.avatar_url,
              name: profile.name
            })
          })

          if (response.ok) {
            const data = await response.json()
            token.accessToken = data.access_token
            token.refreshToken = data.refresh_token
            token.expiresAt = Date.now() + (data.expires_in * 1000)
            token.userId = data.user_id
          } else {
            const errorData = await response.json().catch(() => ({}))
            console.error('Backend authentication failed:', errorData)
            token.error = 'BackendAuthError'
          }
        } catch (error) {
          console.error('Failed to exchange token with backend:', error)
          token.error = 'BackendAuthError'
        }
      }

      // Handle manual token refresh trigger
      if (trigger === "update") {
        return token
      }

      // Check if token needs refresh (1 minute before expiry)
      if (token.expiresAt && Date.now() > (token.expiresAt as number) - 60000) {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh_token: token.refreshToken
            })
          })

          if (response.ok) {
            const data = await response.json()
            token.accessToken = data.access_token
            token.refreshToken = data.refresh_token
            token.expiresAt = Date.now() + (data.expires_in * 1000)
            delete token.error
          } else {
            console.error('Token refresh failed')
            token.error = 'RefreshTokenError'
          }
        } catch (error) {
          console.error('Failed to refresh token:', error)
          token.error = 'RefreshTokenError'
        }
      }

      return token
    },
    async session({ session, token }) {
      // Add backend access token and user ID to session
      if (token.accessToken) {
        session.accessToken = token.accessToken as string
      }
      if (token.userId) {
        session.user.id = token.userId as string
      }
      if (token.error) {
        session.error = token.error as string
      }
      return session
    }
  },
  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },
  session: {
    strategy: "jwt",
    maxAge: 7 * 24 * 60 * 60, // 7 days
  }
})
