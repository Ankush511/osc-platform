/**
 * Lazy-loaded components for code splitting and performance optimization
 *
 * These components are loaded on-demand to reduce initial bundle size
 */
import dynamic from 'next/dynamic';

// Dashboard components - loaded only when user visits dashboard
export const DashboardStats = dynamic(
  () => import('@/components/dashboard/StatsCard'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-32 rounded-lg" />,
    ssr: false,
  }
);

export const ContributionTimeline = dynamic(
  () => import('@/components/dashboard/ContributionTimeline'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded-lg" />,
    ssr: false,
  }
);

export const AchievementBadge = dynamic(
  () => import('@/components/dashboard/AchievementBadge'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-24 rounded-lg" />,
    ssr: false,
  }
);

export const LanguageBreakdown = dynamic(
  () => import('@/components/dashboard/LanguageBreakdown'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

export const RepositoryBreakdown = dynamic(
  () => import('@/components/dashboard/RepositoryBreakdown'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

// Issue components - loaded when viewing issues
export const IssueDetailClient = dynamic(
  () => import('@/components/issues/IssueDetailClient'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-96 rounded-lg" />,
  }
);

export const PRSubmissionForm = dynamic(
  () => import('@/components/issues/PRSubmissionForm'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

export const ContributionCelebration = dynamic(
  () => import('@/components/issues/ContributionCelebration'),
  {
    loading: () => null,
    ssr: false,
  }
);

// Settings components - loaded only when user visits settings
export const PreferencesForm = dynamic(
  () => import('@/components/settings/PreferencesForm'),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded-lg" />,
    ssr: false,
  }
);
