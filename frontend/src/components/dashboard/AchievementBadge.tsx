import { UserAchievementProgress } from '@/types/dashboard'

interface AchievementBadgeProps {
  achievement: UserAchievementProgress
}

export default function AchievementBadge({ achievement }: AchievementBadgeProps) {
  const { achievement: details, progress, is_unlocked, percentage } = achievement

  return (
    <div
      className={`relative p-4 rounded-lg border-2 transition-all ${
        is_unlocked
          ? 'border-green-500 bg-green-50'
          : 'border-gray-300 bg-gray-50 opacity-60'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="text-4xl">{details.badge_icon}</div>
        <div className="flex-1">
          <h3 className={`font-semibold ${is_unlocked ? 'text-gray-900' : 'text-gray-600'}`}>
            {details.name}
          </h3>
          <p className="text-sm text-gray-600 mt-1">{details.description}</p>
          
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{progress} / {details.threshold}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  is_unlocked ? 'bg-green-500' : 'bg-blue-500'
                }`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {is_unlocked && (
        <div className="absolute top-2 right-2">
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Unlocked
          </span>
        </div>
      )}
    </div>
  )
}
