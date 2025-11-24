import { useAuth } from "../contexts/AuthContext";
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  Settings,
  LogOut,
  Cpu,
  BarChart3,
  Shield,
  ChevronDown,
} from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

interface NavigationProps {
  currentPage?: string;
}

export function Navigation({ currentPage }: NavigationProps) {
  const { user, signOut } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      await signOut();
      window.history.pushState({}, "", "/");
      window.dispatchEvent(new PopStateEvent("popstate"));
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  const navigate = (path: string) => {
    window.history.pushState({}, "", path);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const isActive = (page: string) => currentPage === page;

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-[#e3e8ee]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <button
              onClick={() => navigate("/dashboard")}
              className="focus:outline-none rounded-md transition-opacity hover:opacity-80"
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-md flex items-center justify-center">
                  <span className="text-white font-bold text-sm">R</span>
                </div>
                <span className="text-[#0a2540] font-bold text-lg">
                  RekindlePro
                </span>
              </div>
            </button>
          </div>

          {/* Navigation Links - Stripe-style minimal */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => navigate("/dashboard")}
              className={`
                flex items-center gap-2 px-3 py-2
                font-medium text-sm rounded-md
                transition-colors duration-150
                ${
                  isActive("dashboard")
                    ? "text-[#0a2540] bg-[#f6f9fc]"
                    : "text-[#727f96] hover:text-[#0a2540]"
                }
              `}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => navigate("/leads")}
              className={`
                flex items-center gap-2 px-3 py-2
                font-medium text-sm rounded-md
                transition-colors duration-150
                ${
                  isActive("leads")
                    ? "text-[#0a2540] bg-[#f6f9fc]"
                    : "text-[#727f96] hover:text-[#0a2540]"
                }
              `}
            >
              <Users className="w-4 h-4" />
              <span>Leads</span>
            </button>

            <button
              onClick={() => navigate("/campaigns")}
              className={`
                flex items-center gap-2 px-3 py-2
                font-medium text-sm rounded-md
                transition-colors duration-150
                ${
                  isActive("campaigns")
                    ? "text-[#0a2540] bg-[#f6f9fc]"
                    : "text-[#727f96] hover:text-[#0a2540]"
                }
              `}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Campaigns</span>
            </button>

            <button
              onClick={() => navigate("/analytics")}
              className={`
                flex items-center gap-2 px-3 py-2
                font-medium text-sm rounded-md
                transition-colors duration-150
                ${
                  isActive("analytics")
                    ? "text-[#0a2540] bg-[#f6f9fc]"
                    : "text-[#727f96] hover:text-[#0a2540]"
                }
              `}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>
          </div>

          <div className="relative">
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-2 px-3 py-2 text-[#727f96] hover:text-[#0a2540] font-medium text-sm rounded-md transition-colors duration-150"
            >
              <img
                className="w-6 h-6 rounded-full"
                src={`https://ui-avatars.com/api/?name=${
                  user?.email || "User"
                }&background=random`}
                alt="User avatar"
              />
              <ChevronDown className="w-4 h-4" />
            </button>

            {isUserMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-[#e3e8ee] py-1"
              >
                <button
                  onClick={() => navigate("/billing")}
                  className="w-full text-left flex items-center gap-2 px-4 py-2 text-sm text-[#727f96] hover:bg-[#f6f9fc] hover:text-[#0a2540]"
                >
                  <Settings className="w-4 h-4" />
                  <span>Billing</span>
                </button>
                <button
                  onClick={handleSignOut}
                  className="w-full text-left flex items-center gap-2 px-4 py-2 text-sm text-[#727f96] hover:bg-[#f6f9fc] hover:text-[#ef4444]"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Sign out</span>
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
