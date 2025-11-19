interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  className?: string;
}

export function LoadingSpinner({ size = 'md', text, className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 border-2',
    md: 'w-12 h-12 border-3',
    lg: 'w-16 h-16 border-4',
    xl: 'w-24 h-24 border-4',
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-4 ${className}`}>
      <div className="relative">
        <div className={`${sizeClasses[size]} border-primary-200 rounded-full`}></div>
        <div className={`absolute inset-0 ${sizeClasses[size]} border-primary-500 border-t-transparent rounded-full animate-spin`}></div>
      </div>
      {text && (
        <p className="text-gray-700 font-semibold text-lg animate-pulse">{text}</p>
      )}
    </div>
  );
}
