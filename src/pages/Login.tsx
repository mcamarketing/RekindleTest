import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Sparkles } from 'lucide-react';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signIn } = useAuth();

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signIn(email, password);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      if (err instanceof Error) {
        if (err.message.includes('Invalid login credentials')) {
          setError('Invalid email or password. Please check your credentials and try again.');
        } else if (err.message.includes('Email not confirmed')) {
          setError('Please confirm your email address before signing in.');
        } else {
          setError(err.message);
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden flex items-center justify-center px-6">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[800px] h-[800px] bg-[#FF6B35] rounded-full blur-[150px] opacity-30 animate-aurora" />
        <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-[#F7931E] rounded-full blur-[150px] opacity-25 animate-aurora" style={{ animationDelay: '3s' }} />
        <div className="absolute top-1/2 right-1/3 w-[700px] h-[700px] bg-purple-600 rounded-full blur-[150px] opacity-15 animate-aurora" style={{ animationDelay: '6s' }} />
      </div>

      <div className="glass-card p-10 w-full max-w-md animate-fade-in relative z-10">
        <div className="flex items-center justify-center mb-10">
          <img
            src="/images/image copy copy.png"
            alt="Rekindle.ai"
            className="h-20 w-auto"
          />
        </div>

        <h2 className="text-3xl font-bold text-white mb-3 text-center">Welcome back</h2>
        <p className="text-gray-400 mb-8 text-center text-lg">Sign in to your account</p>

        {error && (
          <div className="bg-red-500/20 border border-red-500/30 text-red-300 rounded-xl p-4 mb-6 backdrop-blur-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-bold text-gray-300 mb-3">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FF6B35] transition-all font-medium"
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-bold text-gray-300 mb-3">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-5 py-4 bg-white/5 border border-white/10 text-white placeholder-gray-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#FF6B35] transition-all font-medium"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white rounded-xl font-bold text-lg hover:shadow-2xl hover:shadow-[#FF6B35]/40 transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 btn-shimmer"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-8 text-center text-gray-400">
          Don't have an account?{' '}
          <button
            onClick={() => navigate('/signup')}
            className="text-[#FF6B35] font-bold hover:text-[#F7931E] transition-colors"
          >
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
}
