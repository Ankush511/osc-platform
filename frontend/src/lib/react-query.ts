/**
 * React Query configuration for data fetching and caching
 */
import { QueryClient, DefaultOptions } from '@tanstack/react-query';

// Default query options for optimal caching
const defaultOptions: DefaultOptions = {
  queries: {
    // Cache data for 5 minutes by default
    staleTime: 5 * 60 * 1000,
    
    // Keep unused data in cache for 10 minutes
    gcTime: 10 * 60 * 1000,
    
    // Retry failed requests
    retry: 1,
    
    // Refetch on window focus for fresh data
    refetchOnWindowFocus: true,
    
    // Don't refetch on mount if data is fresh
    refetchOnMount: false,
    
    // Don't refetch on reconnect if data is fresh
    refetchOnReconnect: false,
  },
  mutations: {
    // Retry failed mutations once
    retry: 1,
  },
};

// Create query client with default options
export const queryClient = new QueryClient({
  defaultOptions,
});

// Query keys for consistent cache management
export const queryKeys = {
  // User queries
  user: {
    me: ['user', 'me'] as const,
    stats: (userId: number) => ['user', 'stats', userId] as const,
    achievements: (userId: number) => ['user', 'achievements', userId] as const,
    timeline: (userId: number) => ['user', 'timeline', userId] as const,
  },
  
  // Issue queries
  issues: {
    all: ['issues'] as const,
    list: (filters: Record<string, any>) => ['issues', 'list', filters] as const,
    detail: (issueId: number) => ['issues', 'detail', issueId] as const,
    claimed: (userId: number) => ['issues', 'claimed', userId] as const,
  },
  
  // Repository queries
  repositories: {
    all: ['repositories'] as const,
    detail: (repoId: number) => ['repositories', 'detail', repoId] as const,
  },
  
  // Contribution queries
  contributions: {
    all: ['contributions'] as const,
    byUser: (userId: number) => ['contributions', 'user', userId] as const,
    detail: (contributionId: number) => ['contributions', 'detail', contributionId] as const,
  },
  
  // AI queries
  ai: {
    repoSummary: (repoId: number) => ['ai', 'repo-summary', repoId] as const,
    issueExplanation: (issueId: number) => ['ai', 'issue-explanation', issueId] as const,
  },
};

// Cache invalidation helpers
export const invalidateQueries = {
  user: (userId: number) => {
    queryClient.invalidateQueries({ queryKey: queryKeys.user.stats(userId) });
    queryClient.invalidateQueries({ queryKey: queryKeys.user.achievements(userId) });
    queryClient.invalidateQueries({ queryKey: queryKeys.user.timeline(userId) });
  },
  
  issues: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.issues.all });
  },
  
  issue: (issueId: number) => {
    queryClient.invalidateQueries({ queryKey: queryKeys.issues.detail(issueId) });
  },
  
  contributions: (userId: number) => {
    queryClient.invalidateQueries({ queryKey: queryKeys.contributions.byUser(userId) });
  },
};

// Prefetch helpers for optimistic loading
export const prefetchQueries = {
  issueDetail: async (issueId: number, fetcher: () => Promise<any>) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.issues.detail(issueId),
      queryFn: fetcher,
      staleTime: 5 * 60 * 1000,
    });
  },
  
  userStats: async (userId: number, fetcher: () => Promise<any>) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.user.stats(userId),
      queryFn: fetcher,
      staleTime: 15 * 60 * 1000,
    });
  },
};
