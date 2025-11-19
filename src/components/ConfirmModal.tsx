import { AlertTriangle, X } from 'lucide-react';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
}

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger'
}: ConfirmModalProps) {
  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      gradient: 'from-red-500 to-rose-600',
      glow: 'shadow-red-500/50',
      icon: 'text-red-400',
    },
    warning: {
      gradient: 'from-yellow-500 to-orange-600',
      glow: 'shadow-yellow-500/50',
      icon: 'text-yellow-400',
    },
    info: {
      gradient: 'from-blue-500 to-cyan-600',
      glow: 'shadow-blue-500/50',
      icon: 'text-blue-400',
    },
  };

  const style = variantStyles[variant];

  return (
    <div
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center px-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border-2 border-white/10 rounded-3xl p-8 max-w-md w-full relative animate-scale-in shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 glass-morphism rounded-full hover:bg-white/20 transition-all group"
        >
          <X className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
        </button>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className={`p-4 rounded-2xl bg-gradient-to-br ${style.gradient} shadow-2xl ${style.glow}`}>
            <AlertTriangle className="w-12 h-12 text-white" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-black text-white text-center mb-4">
          {title}
        </h2>

        {/* Message */}
        <p className="text-gray-300 text-center mb-8">
          {message}
        </p>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 glass-morphism text-white font-bold rounded-xl hover:bg-white/20 transition-all"
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`flex-1 px-6 py-3 bg-gradient-to-r ${style.gradient} text-white font-bold rounded-xl hover:shadow-2xl hover:${style.glow} transition-all hover:scale-105`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
