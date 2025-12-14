import { useEffect, useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import LandingPage from './pages/LandingPage';
import LandingPageNew from './pages/LandingPageNew';
import RekindleProLanding from './pages/RekindleProLanding';
import RekindleProApple from './pages/RekindleProApple';
import AboutPro from './pages/AboutPro';
import PlatformPro from './pages/PlatformPro';
import IntelligencePro from './pages/IntelligencePro';
import PilotApplicationPro from './pages/PilotApplicationPro';
import { SignUp } from './pages/SignUp';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { DashboardNew } from './pages/DashboardNew';
import { SimpleLeads as Leads } from './pages/Leads';
import { Leads as LeadsNew } from './pages/LeadsNew';
import { LeadDetail } from './pages/LeadDetail';
import { Campaigns } from './pages/Campaigns';
import { CampaignsNew } from './pages/CampaignsNew';
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
import { Domains } from './pages/Domains';
import { About } from './pages/About';
import { PilotApplication } from './pages/PilotApplication';
import { RevivalMessages } from './pages/RevivalMessages';
import { RevivalDashboard } from './pages/RevivalDashboard';
import { EmailSettings } from './pages/EmailSettings';
import { MVPConsole } from './pages/MVPConsole';
import AssistantChat from './components/AssistantChat';
import { AppShell } from './layouts/AppShell';
import { AuthLayout } from './layouts/AuthLayout';
import { Globe, Plus } from 'lucide-react';

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

  // RekindlePro marketing pages
  if (route === '/about') {
    return <AboutPro />;
  }

  if (route === '/platform') {
    return <PlatformPro />;
  }

  if (route === '/intelligence') {
    return <IntelligencePro />;
  }

  if (route === '/pilot-application') {
    return <PilotApplicationPro />;
  }

  // Legacy routes
  if (route === '/about-old') {
    return <About />;
  }

  if (route === '/pilot-application-old') {
    return <PilotApplication />;
  }

  // Landing page routes
  if (route === '/trust' || route === '/original' || route === '/old') {
    return <LandingPage />;
  }

  // New conversion-optimized landing page
  if (route === '/new' || route === '/v2') {
    return <LandingPageNew />;
  }

  // Apple-style premium landing page
  if (route === '/rekindlepro-apple' || route === '/apple') {
    return <RekindleProApple />;
  }

  // RekindlePro landing with WebGL
  if (route === '/rekindlepro') {
    return <RekindleProLanding />;
  }

  if (user) {
    // Redirect root/login/signup to dashboard for authenticated users
    if (route === '/' || route === '/login' || route === '/signup') {
      window.history.pushState({}, '', '/dashboard');
      return (
        <AppShell>
          <Dashboard />
        </AppShell>
      );
    }

    // Dashboard routes with AppShell
    if (route === '/dashboard') {
      return (
        <AppShell>
          <DashboardNew />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/dashboard/campaigns') {
      return (
        <AppShell>
          <CampaignsNew />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/dashboard/campaigns/new') {
      return (
        <AppShell>
          <CreateCampaign />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route.startsWith('/dashboard/campaigns/') && route !== '/dashboard/campaigns/new') {
      return (
        <AppShell>
          <CampaignDetail />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/dashboard/leads') {
      return (
        <AppShell>
          <LeadsNew />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/dashboard/leads/import') {
      return (
        <AppShell>
          <LeadImport />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route.startsWith('/dashboard/leads/') && route !== '/dashboard/leads/import') {
      const leadId = route.split('/dashboard/leads/')[1];
      return (
        <AppShell>
          <LeadDetail leadId={leadId} />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/revival/messages') {
      return (
        <AppShell>
          <RevivalMessages />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/revival/dashboard') {
      return (
        <AppShell>
          <RevivalDashboard />
          <AssistantChat />
        </AppShell>
      );
    }

    // Legacy /leads route - redirect to /dashboard/leads but also support direct access
    if (route === '/leads') {
      return (
        <AppShell>
          <LeadsNew />
          <AssistantChat />
        </AppShell>
      );
    }

    // MVP Console route
    if (route === '/mvp') {
      return <MVPConsole />;
    }

    // Email settings route
    if (route === '/settings/email') {
      return (
        <AppShell>
          <EmailSettings />
          <AssistantChat />
        </AppShell>
      );
    }    if (route === '/dashboard/domains') { 

      return (
        <AppShell>
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Domains & Inboxes</h1>
              <button className="inline-flex items-center px-4 py-2 bg-orange-500 text-white text-sm font-medium rounded-lg hover:bg-orange-600 transition-colors">
                <Plus className="w-4 h-4 mr-2" />
                Add Domain
              </button>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
              <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Domain Management</h3>
              <p className="text-gray-600">Domain and inbox management interface coming soon.</p>
            </div>
          </div>
        </AppShell>
      );
    }

    if (route === '/dashboard/rex') {
      return (
        <AppShell>
          <AIAgents />
          <AssistantChat />
        </AppShell>
      );
    }

    if (route === '/dashboard/settings') {
      return (
        <AppShell>
          <Billing />
          <AssistantChat />
        </AppShell>
      );
    }

    // Legacy routes - redirect to new structure
    if (route === '/leads/import') {
      window.history.pushState({}, '', '/dashboard/leads/import');
      return (
        <AppShell>
          <LeadImport />
        </AppShell>
      );
    }

    // Legacy /leads redirect handled above

    if (route.startsWith('/leads/')) {
      const leadId = route.split('/leads/')[1];
      window.history.pushState({}, '', `/dashboard/leads/${leadId}`);
      return (
        <AppShell>
          <LeadDetail leadId={leadId} />
        </AppShell>
      );
    }

    if (route === '/campaigns') {
      window.history.pushState({}, '', '/dashboard/campaigns');
      return (
        <AppShell>
          <Campaigns />
        </AppShell>
      );
    }

    if (route === '/campaigns/create') {
      window.history.pushState({}, '', '/dashboard/campaigns/new');
      return (
        <AppShell>
          <CreateCampaign />
        </AppShell>
      );
    }

    if (route.startsWith('/campaigns/') && route !== '/campaigns/create') {
      window.history.pushState({}, '', `/dashboard${route}`);
      return (
        <AppShell>
          <CampaignDetail />
        </AppShell>
      );
    }

    if (route === '/billing') {
      window.history.pushState({}, '', '/dashboard/settings');
      return (
        <AppShell>
          <Billing />
        </AppShell>
      );
    }

    if (route === '/agents') {
      window.history.pushState({}, '', '/dashboard/rex');
      return (
        <AppShell>
          <AIAgents />
        </AppShell>
      );
    }

    if (route === '/analytics') {
      window.history.pushState({}, '', '/dashboard');
      return (
        <AppShell>
          <Dashboard />
        </AppShell>
      );
    }

    if (route === '/compliance') {
      window.history.pushState({}, '', '/dashboard/settings');
      return (
        <AppShell>
          <SuppressionList />
        </AppShell>
      );
    }

    // Default dashboard
    return (
      <AppShell>
        <Dashboard />
        <AssistantChat />
      </AppShell>
    );
  }

  if (route === '/signup') {
    return (
      <AuthLayout
        title="Create your account"
        subtitle="Start your free 30-day trial. No credit card required."
      >
        <SignUp />
      </AuthLayout>
    );
  }

  if (route === '/login') {
    return (
      <AuthLayout
        title="Sign in to RekindlePro"
        subtitle="Welcome back. Enter your credentials to continue."
      >
        <Login />
      </AuthLayout>
    );
  }

  // Default: New conversion-optimized landing page
  return <LandingPageNew />;
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
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;




