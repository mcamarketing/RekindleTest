import { CheckCircle2, Mail, Users, TrendingUp } from 'lucide-react';

interface Activity {
  id: string;
  type: 'lead_imported' | 'campaign_started' | 'meeting_booked' | 'lead_responded';
  message: string;
  timestamp: string;
  icon: 'check' | 'mail' | 'users' | 'trending';
}

const iconMap = {
  check: CheckCircle2,
  mail: Mail,
  users: Users,
  trending: TrendingUp,
};

const colorMap = {
  check: 'from-green-500 to-emerald-600',
  mail: 'from-blue-500 to-blue-600',
  users: 'from-purple-500 to-purple-600',
  trending: 'from-orange-500 to-orange-600',
};

interface ActivityFeedProps {
  activities: Activity[];
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  if (activities.length === 0) {
    return (
      <div className="glass-card p-10 animate-fade-in">
        <h2 className="text-2xl font-bold text-white mb-6">Recent Activity</h2>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-gray-400 text-lg">No recent activity yet</p>
          <p className="text-gray-500 text-sm mt-2">Start importing leads to see your activity here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-10 animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Recent Activity</h2>
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </span>
      </div>
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = iconMap[activity.icon];
          const gradient = colorMap[activity.icon];

          return (
            <div
              key={activity.id}
              className="flex items-start gap-4 p-4 rounded-xl glass-morphism hover:bg-white/5 transition-all duration-300 animate-slide-in-left"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className={`p-2 bg-gradient-to-br ${gradient} rounded-lg flex-shrink-0`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-white font-medium">{activity.message}</p>
                <p className="text-gray-500 text-sm mt-1">{activity.timestamp}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

