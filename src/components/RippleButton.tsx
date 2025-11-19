import { ButtonHTMLAttributes } from 'react';

interface RippleButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function RippleButton({
  variant = 'primary',
  size = 'md',
  children,
  className = '',
  disabled,
  ...props
}: RippleButtonProps) {
  const variantClasses = {
    primary: 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white hover:shadow-lg btn-shimmer',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    outline: 'border-2 border-[#FF6B35] text-[#FF6B35] hover:bg-orange-50',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <button
      className={`
        relative overflow-hidden rounded-lg font-semibold
        transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-4 focus:ring-orange-200
        hover:scale-[1.02] active:scale-[0.98]
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      disabled={disabled}
      {...props}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </button>
  );
}
