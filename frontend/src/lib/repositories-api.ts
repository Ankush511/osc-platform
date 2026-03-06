import { Repository } from '@/types/repository'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchRepositoryById(
  repositoryId: number,
  accessToken: string
): Promise<Repository> {
  const response = await fetch(`${API_URL}/api/v1/repositories/${repositoryId}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
    cache: 'no-store',
  })
  
  if (!response.ok) {
    throw new Error(`Failed to fetch repository: ${response.statusText}`)
  }
  
  return response.json()
}
