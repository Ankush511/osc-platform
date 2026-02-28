interface LanguageBreakdownProps {
  contributions: Record<string, number>
}

export default function LanguageBreakdown({ contributions }: LanguageBreakdownProps) {
  const languages = Object.entries(contributions).sort((a, b) => b[1] - a[1])
  const total = languages.reduce((sum, [_, count]) => sum + count, 0)

  const getLanguageColor = (language: string) => {
    const colors: Record<string, string> = {
      Python: 'bg-blue-500',
      JavaScript: 'bg-yellow-500',
      TypeScript: 'bg-blue-600',
      Go: 'bg-cyan-500',
      Rust: 'bg-orange-600',
      Java: 'bg-red-500',
      'C++': 'bg-pink-500',
      Ruby: 'bg-red-600',
      PHP: 'bg-purple-500',
    }
    return colors[language] || 'bg-gray-500'
  }

  if (languages.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No language data available yet
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {languages.map(([language, count]) => {
        const percentage = (count / total) * 100
        return (
          <div key={language}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">{language}</span>
              <span className="text-sm text-gray-600">
                {count} ({percentage.toFixed(1)}%)
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full ${getLanguageColor(language)}`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
