/**
 * Lazy-loaded components for code splitting and performance optimization
 * 
 * These components are loaded on-demand to reduce initial bundle size
 */
import dynamic from 'next/dynamic';

// Dashboard components - loaded only when user visits dashboard
export const DashboardStats = dynamic(
  () => import('@/components/dashboard/StatsCard').then(mod => ({ default: mod.StatsCard })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-32 rounded-lg" />,
    ssr: false,
  }
);

export const ContributionTimeline = dynamic(
  () => import('@/components/dashboard/ContributionTimeline').then(mod => ({ default: mod.ContributionTimeline })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded-lg" />,
    ssr: false,
  }
);

export const AchievementBadge = dynamic(
  () => import('@/components/dashboard/AchievementBadge').then(mod => ({ default: mod.AchievementBadge })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-24 rounded-lg" />,
    ssr: false,
  }
);

export const LanguageBreakdown = dynamic(
  () => import('@/components/dashboard/LanguageBreakdown').then(mod => ({ default: mod.LanguageBreakdown })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

export const RepositoryBreakdown = dynamic(
  () => import('@/components/dashboard/RepositoryBreakdown').then(mod => ({ default: mod.RepositoryBreakdown })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

// Issue components - loaded when viewing issues
export const IssueDetailClient = dynamic(
  () => import('@/components/issues/IssueDetailClient').then(mod => ({ default: mod.IssueDetailClient })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-96 rounded-lg" />,
  }
);

export const PRSubmissionForm = dynamic(
  () => import('@/components/issues/PRSubmissionForm').then(mod => ({ default: mod.PRSubmissionForm })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-48 rounded-lg" />,
    ssr: false,
  }
);

export const ContributionCelebration = dynamic(
  () => import('@/components/issues/ContributionCelebration').then(mod => ({ default: mod.ContributionCelebration })),
  {
    loading: () => null,
    ssr: false,
  }
);

// Settings components - loaded only when user visits settings
export const PreferencesForm = dynamic(
  () => import('@/components/settings/PreferencesForm').then(mod => ({ default: mod.PreferencesForm })),
  {
    loading: () => <div className="animate-pulse bg-gray-200 h-64 rounded-lg" />,
    ssr: false,
  }
);
