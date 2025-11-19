import { Navigation } from '../components/Navigation';
import { User } from 'lucide-react';

export function LeadDetail({ leadId }: { leadId: string }) {
  return (
    <div className="min-h-screen bg-[#1A1F2E] relative overflow-hidden">
      {/* Aurora gradient backgrounds */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[800px] h-[800px] bg-purple-600 rounded-full blur-[150px] opacity-15 animate-aurora" />
        <div className="absolute top-1/3 left-1/4 w-[600px] h-[600px] bg-[#FF6B35] rounded-full blur-[150px] opacity-20 animate-aurora" style={{ animationDelay: '4s' }} />
        <div className="absolute bottom-1/4 right-1/3 w-[700px] h-[700px] bg-blue-600 rounded-full blur-[150px] opacity-10 animate-aurora" style={{ animationDelay: '7s' }} />
      </div>

      <Navigation currentPage="leads" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="glass-card p-12 text-center animate-fade-in">
          <div className="p-6 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-3xl w-fit mx-auto mb-6 shadow-2xl">
            <User className="w-20 h-20 text-white" />
          </div>
          <h1 className="text-4xl font-black text-white mb-3">Lead Detail</h1>
          <p className="text-gray-300 text-lg mb-4">Viewing details for lead:</p>
          <p className="text-2xl font-bold text-[#FF6B35]">{leadId}</p>
          <p className="text-gray-400 mt-6">Detailed lead information will be displayed here</p>
        </div>
      </main>
    </div>
  );
}
