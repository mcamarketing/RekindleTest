import { useAuth } from '../contexts/AuthContext';
import { LayoutDashboard, Users, TrendingUp, Settings, LogOut, Cpu, BarChart3, Shield } from 'lucide-react';

interface NavigationProps {
  currentPage?: string;
}

export function Navigation({ currentPage }: NavigationProps) {
  const { signOut } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
      window.history.pushState({}, '', '/');
      window.dispatchEvent(new PopStateEvent('popstate'));
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const isActive = (page: string) => currentPage === page;

  return (
    <nav className="sticky top-0 z-50 bg-[#1A1F2E]/95 backdrop-blur-xl border-b border-gray-800 shadow-2xl">
      {/* Aurora gradient background effect */}
      <div className="absolute inset-0 opacity-30 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-[#FF6B35] rounded-full blur-[120px] animate-aurora" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#F7931E] rounded-full blur-[120px] animate-aurora" style={{ animationDelay: '2s' }} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="focus:outline-none focus:ring-2 focus:ring-[#FF6B35]/50 rounded-lg transition-all duration-300 hover:scale-105"
            >
              <img
                src="/images/image copy copy.png"
                alt="Rekindle.ai"
                className="h-12 w-auto"
              />
            </button>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => navigate('/dashboard')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('dashboard')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => navigate('/leads')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('leads')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <Users className="w-4 h-4" />
              <span>Leads</span>
            </button>

            <button
              onClick={() => navigate('/campaigns')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('campaigns')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Campaigns</span>
            </button>

            <button
              onClick={() => navigate('/agents')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('agents')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <Cpu className="w-4 h-4" />
              <span>AI Agents</span>
            </button>

            <button
              onClick={() => navigate('/analytics')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('analytics')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>

            <button
              onClick={() => navigate('/billing')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('billing')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <Settings className="w-4 h-4" />
              <span>Billing</span>
            </button>

            <button
              onClick={() => navigate('/compliance')}
              className={`
                flex items-center gap-2 px-4 py-2.5
                font-semibold text-sm rounded-xl
                transition-all duration-300
                ${isActive('compliance')
                  ? 'text-white bg-gradient-to-r from-[#FF6B35] to-[#F7931E] shadow-lg shadow-[#FF6B35]/30 scale-105'
                  : 'text-gray-400 hover:text-white hover:bg-white/5 hover:shadow-lg hover:shadow-white/10'
                }
              `}
            >
              <Shield className="w-4 h-4" />
              <span>Compliance</span>
            </button>

            <div className="w-px h-8 bg-gray-700 mx-2" />

            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 px-4 py-2.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 font-semibold text-sm rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
