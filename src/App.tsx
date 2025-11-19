import { useEffect, useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LandingPage } from './pages/LandingPage';
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

  // Default: Trust-first landing page
  return <TrustLandingPage />;
  })();

  return (
    <ErrorBoundary>
      <ToastProvider>
        {content}
        <AIAgentWidget />
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
