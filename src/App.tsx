import { useEffect, useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import LandingPagePremium from './pages/LandingPagePremium';
import { TrustLandingPage } from './pages/TrustLandingPage';
import { SignUp } from './pages/SignUp';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Leads } from './pages/Leads';
import { LeadDetail } from './pages/LeadDetail';
import { Campaigns } from './pages/Campaigns';
import { CampaignDetail } from './pages/CampaignDetail';
import { CreateCampaign } from './pages/CreateCampaign';
import { LeadImport } from './pages/LeadImport';
import { Billing } from './pages/Billing';
import { AIAgents } from './pages/AIAgents';
import { Analytics } from './pages/Analytics';
import { PrivacyPolicy } from './pages/PrivacyPolicy';
import { TermsOfService } from './pages/TermsOfService';
import { Blog } from './pages/Blog';
import { Unsubscribe } from './pages/Unsubscribe';
import { PreferenceCenter } from './pages/PreferenceCenter';
import { SuppressionList } from './pages/SuppressionList';
import { About } from './pages/About';
import { PilotApplication } from './pages/PilotApplication';
import { AIAgentWidget } from './components/AIAgentWidget';
import { EnhancedChatWidget } from './components/enhanced/EnhancedChatWidget';

function App() {
  const { user, loading } = useAuth();
  const [route, setRoute] = useState(window.location.pathname);

  useEffect(() => {
    const handleRouteChange = () => {
      setRoute(window.location.pathname);
    };

    window.addEventListener('popstate', handleRouteChange);

    const originalPushState = window.history.pushState;
    window.history.pushState = function(...args) {
      originalPushState.apply(window.history, args);
      handleRouteChange();
    };

    return () => {
      window.removeEventListener('popstate', handleRouteChange);
      window.history.pushState = originalPushState;
    };
  }, []);

  if (loading) {
    return (
      <ToastProvider>
        <div className="min-h-screen bg-gradient-to-br from-primary-500 via-secondary-500 to-primary-500 flex items-center justify-center">
          <div className="text-center">
            <div className="relative">
              <div className="w-20 h-20 border-4 border-white/30 rounded-full"></div>
              <div className="absolute inset-0 w-20 h-20 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-white font-bold text-lg mt-6 animate-pulse">Loading...</p>
          </div>
        </div>
      </ToastProvider>
    );
  }

  const content = (() => {
  // Public routes accessible to everyone
  if (route === '/privacy') {
    return <PrivacyPolicy />;
  }

  if (route === '/terms') {
    return <TermsOfService />;
  }

  if (route === '/blog') {
    return <Blog />;
  }

  if (route === '/unsubscribe') {
    return <Unsubscribe />;
  }

  if (route === '/preferences') {
    return <PreferenceCenter />;
  }

  if (route === '/about') {
    return <About />;
  }

  if (route === '/pilot-application') {
    return <PilotApplication />;
  }

  // Trust-first landing page (new default)
  if (route === '/trust') {
    return <TrustLandingPage />;
  }

  // Original landing page (for comparison)
  if (route === '/original') {
    return <LandingPage />;
  }

  if (user) {
    if (route === '/' || route === '/login' || route === '/signup') {
      window.history.pushState({}, '', '/dashboard');
      return <Dashboard />;
    }

    if (route === '/leads/import') {
      return <LeadImport />;
    }

    if (route === '/leads') {
      return <Leads />;
    }

    if (route.startsWith('/leads/')) {
      const leadId = route.split('/leads/')[1];
      return <LeadDetail leadId={leadId} />;
    }

    if (route === '/campaigns') {
      return <Campaigns />;
    }

    if (route === '/campaigns/create') {
      return <CreateCampaign />;
    }

    if (route.startsWith('/campaigns/') && route !== '/campaigns/create') {
      return <CampaignDetail />;
    }

    if (route === '/billing') {
      return <Billing />;
    }

    if (route === '/agents') {
      return <AIAgents />;
    }

    if (route === '/analytics') {
      return <Analytics />;
    }

    if (route === '/compliance') {
      return <SuppressionList />;
    }

    if (route === '/dashboard') {
      return <Dashboard />;
    }

    return <Dashboard />;
  }

  if (route === '/signup') {
    return <SignUp />;
  }

  if (route === '/login') {
    return <Login />;
  }

  // Default: Premium Stripe/Linear/Apple-quality landing page
  return <LandingPagePremium />;
  })();

  // Chat widget message handler
  const handleChatMessage = async (message: string): Promise<string> => {
    // TODO: Integrate with actual AI backend
    // For now, return a helpful response
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay

    if (message.toLowerCase().includes('pilot') || message.toLowerCase().includes('apply')) {
      return "I'd be happy to help you with our pilot program! You can apply at /pilot-application. The pilot includes Month 1 complimentary access, performance-based pricing, and founding member rates locked permanently. Would you like me to share more details?";
    } else if (message.toLowerCase().includes('price') || message.toLowerCase().includes('cost')) {
      return "We offer performance-based pricing - you only pay for confirmed meetings with decision-makers. Founding pilot members lock in permanent rates. Would you like to schedule a call to discuss pricing for your specific needs?";
    } else if (message.toLowerCase().includes('lead') || message.toLowerCase().includes('reactivat')) {
      return "RekindlePro specializes in dead lead reactivation using AI. Our system monitors 50+ trigger events per lead and automatically re-engages them at the perfect moment. On average, we help clients reactivate 25-30% of dormant leads. Want to learn more?";
    } else if (message.toLowerCase().includes('meeting') || message.toLowerCase().includes('demo')) {
      return "I can help schedule a demo! Please visit our pilot application page at /pilot-application or email us at pilot@rekindlepro.ai with your preferred times. Our team typically responds within 4 hours.";
    } else {
      return `Thanks for your message! I'm here to help with questions about RekindlePro's AI-powered lead reactivation platform. I can assist with:\n\n• Pilot program details\n• Pricing and ROI\n• Lead reactivation strategies\n• Platform features\n• Scheduling a demo\n\nWhat would you like to know more about?`;
    }
  };

  return (
    <ErrorBoundary>
      <ToastProvider>
        {content}
        <AIAgentWidget />
        <EnhancedChatWidget onSendMessage={handleChatMessage} />
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
