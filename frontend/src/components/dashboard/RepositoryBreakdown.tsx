interface RepositoryBreakdownProps {
  contributions: Record<string, number>
}

export default function RepositoryBreakdown({ contributions }: RepositoryBreakdownProps) {
  const repositories = Object.entries(contributions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10) // Show top 10 repositories

  if (repositories.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No repository data available yet
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {repositories.map(([repo, count]) => (
        <div
          key={repo}
          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <span className="text-gray-400">📦</span>
            <a
              href={`https://github.com/${repo}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-gray-900 hover:text-blue-600 truncate"
            >
              {repo}
            </a>
          </div>
          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {count} {count === 1 ? 'contribution' : 'contributions'}
          </span>
        </div>
      ))}
    </div>
  )
}
