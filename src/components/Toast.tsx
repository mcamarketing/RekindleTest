import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  showToast: (toast: Omit<Toast, 'id'>) => void;
  hideToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(7);
    const newToast = { ...toast, id };

    setToasts((prev) => [...prev, newToast]);

    const duration = toast.duration || 5000;
    setTimeout(() => {
      hideToast(id);
    }, duration);
  }, []);

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const icons = {
    success: CheckCircle2,
    error: AlertCircle,
    info: Info,
    warning: AlertTriangle,
  };

  const colors = {
    success: {
      gradient: 'from-green-500 to-emerald-600',
      glow: 'shadow-green-500/50',
      icon: 'text-green-400',
      text: 'text-white',
    },
    error: {
      gradient: 'from-red-500 to-rose-600',
      glow: 'shadow-red-500/50',
      icon: 'text-red-400',
      text: 'text-white',
    },
    info: {
      gradient: 'from-blue-500 to-cyan-600',
      glow: 'shadow-blue-500/50',
      icon: 'text-blue-400',
      text: 'text-white',
    },
    warning: {
      gradient: 'from-yellow-500 to-orange-600',
      glow: 'shadow-yellow-500/50',
      icon: 'text-yellow-400',
      text: 'text-white',
    },
  };

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none">
        {toasts.map((toast) => {
          const Icon = icons[toast.type];
          const color = colors[toast.type];

          return (
            <div
              key={toast.id}
              className={`
                pointer-events-auto max-w-md rounded-2xl
                bg-slate-900/95 backdrop-blur-xl border border-white/10
                shadow-2xl ${color.glow}
                animate-slide-in-right
                relative overflow-hidden
              `}
            >
              {/* Gradient accent */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${color.gradient}`} />

              <div className="flex items-start gap-4 p-4 pt-5">
                <div className={`p-2 rounded-xl bg-gradient-to-br ${color.gradient} shadow-lg`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`font-bold ${color.text} text-lg`}>{toast.title}</p>
                  {toast.message && (
                    <p className="text-sm mt-1 text-gray-300">
                      {toast.message}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => hideToast(toast.id)}
                  className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-white/10 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}
