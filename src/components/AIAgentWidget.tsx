import { useState, useRef, useEffect } from 'react';
import {
  MessageCircle, X, Send, Sparkles, Minimize2, Menu, HelpCircle, Zap,
  TrendingUp, DollarSign, ArrowLeft, Mic, MicOff, Activity, Brain,
  Target, BarChart3, Users, Globe, Lightbulb, TrendingDown, Clock,
  CheckCircle2, AlertCircle, Loader2
} from 'lucide-react';
import { apiClient } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  type?: 'text' | 'insight' | 'suggestion' | 'alert';
  metadata?: {
    icon?: React.ReactNode;
    actionable?: boolean;
    priority?: 'low' | 'medium' | 'high';
  };
}

interface FAQ {
  question: string;
  answer: string;
  shortcut?: string;
  category?: string;
}

interface AgentInsight {
  type: 'opportunity' | 'warning' | 'tip' | 'achievement';
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: () => void;
  actionLabel?: string;
}

const FAQs: FAQ[] = [
  {
    question: "How do I import leads?",
    answer: "Go to the Leads page and click 'Import Leads'. Upload a CSV file with columns like name, email, company, and phone. Our AI will automatically score and categorize them.",
    category: "Getting Started"
  },
  {
    question: "How do I create a campaign?",
    answer: "Navigate to Campaigns → Create Campaign → Select your leads → Choose channels → Launch. The AI handles message generation automatically.",
    category: "Campaigns"
  },
  {
    question: "What's the pricing?",
    answer: "Starter plan is $99/month. We also offer performance-based pricing at 2.5% of closed deals. Most users see strong ROI within 90 days.",
    category: "Billing"
  },
  {
    question: "How does lead scoring work?",
    answer: "Our AI analyzes lead data, company information, engagement signals, and research to assign scores from 0-100. Higher scores indicate better opportunities.",
    category: "Leads"
  },
  {
    question: "What channels do you support?",
    answer: "We support Email, SMS, WhatsApp, and Push notifications. You can use multiple channels in a single campaign for maximum reach.",
    category: "Features"
  },
  {
    question: "How long until I see results?",
    answer: "Most users see their first reactivated lead respond within 48 hours. Campaign performance typically stabilizes within 1-2 weeks.",
    category: "Results"
  }
];

export function AIAgentWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [userName, setUserName] = useState<string | null>(null);
  const [userFirstName, setUserFirstName] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [agentMood, setAgentMood] = useState<'happy' | 'thinking' | 'celebrating' | 'focused'>('happy');
  const [insights, setInsights] = useState<AgentInsight[]>([]);
  const [showInsights, setShowInsights] = useState(false);

  // Fetch user profile to get name
  useEffect(() => {
    const fetchUserName = async () => {
      if (user?.id) {
        try {
          const { data, error } = await supabase
            .from('profiles')
            .select('first_name, last_name, full_name')
            .eq('id', user.id)
            .single();

          if (data && !error) {
            const firstName = data.first_name ||
                             (data.full_name ? data.full_name.split(' ')[0] : null) ||
                             (user.email ? user.email.split('@')[0] : null);
            setUserFirstName(firstName);
            setUserName(data.full_name || `${data.first_name || ''} ${data.last_name || ''}`.trim() || firstName);
          } else {
            const emailName = user.email?.split('@')[0] || null;
            setUserFirstName(emailName);
            setUserName(emailName);
          }
        } catch (error) {
          console.error('Error fetching user name:', error);
          const emailName = user.email?.split('@')[0] || null;
          setUserFirstName(emailName);
          setUserName(emailName);
        }
      }
    };

    fetchUserName();
  }, [user]);

  // Generate contextual insights
  useEffect(() => {
    if (user && isOpen) {
      generateInsights();
    }
  }, [user, isOpen]);

  const generateInsights = async () => {
    const newInsights: AgentInsight[] = [];

    // Get user stats for contextual insights
    try {
      const { count: leadsCount } = await supabase
        .from('leads')
        .select('*', { count: 'exact', head: true });

      const { count: campaignsCount } = await supabase
        .from('campaigns')
        .select('*', { count: 'exact', head: true })
        .eq('status', 'active');

      if (!leadsCount || leadsCount === 0) {
        newInsights.push({
          type: 'tip',
          title: 'Get Started with Leads',
          description: 'Import your first leads to unlock the full power of Rekindle AI',
          icon: <Users className="w-5 h-5" />,
          action: () => window.history.pushState({}, '', '/leads/import'),
          actionLabel: 'Import Leads'
        });
      }

      if (leadsCount && leadsCount > 0 && (!campaignsCount || campaignsCount === 0)) {
        newInsights.push({
          type: 'opportunity',
          title: 'Ready to Launch',
          description: `You have ${leadsCount} leads waiting. Create your first campaign to start reactivating them!`,
          icon: <Zap className="w-5 h-5" />,
          action: () => window.history.pushState({}, '', '/campaigns/create'),
          actionLabel: 'Create Campaign'
        });
      }

      if (campaignsCount && campaignsCount > 0) {
        newInsights.push({
          type: 'achievement',
          title: 'Campaigns Running',
          description: `${campaignsCount} active campaign${campaignsCount > 1 ? 's' : ''} working for you 24/7`,
          icon: <CheckCircle2 className="w-5 h-5" />,
        });
      }

      setInsights(newInsights);
    } catch (error) {
      console.error('Error generating insights:', error);
    }
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
    const name = userFirstName || (user ? 'there' : '');

    if (user) {
      return name
        ? `${greeting}, ${name}! 🚀\n\nI'm Rex, your Rekindle AI Expert. I'm powered by Claude Sonnet 4.5 and I orchestrate 28 specialized AI agents working 24/7 to reactivate your dormant leads.\n\n🎯 **What I Can Do:**\n• Analyze your lead database and identify high-value opportunities\n• Create and optimize multi-channel campaigns (Email, SMS, WhatsApp)\n• Monitor 50+ signals for trigger events (funding, hiring, job changes)\n• Generate personalized messages with deep research insights\n• Track performance and provide real-time optimization recommendations\n• Handle objections and book meetings automatically\n• Ensure compliance (GDPR, CAN-SPAM, CCPA)\n\n💡 **My Capabilities:**\nI leverage our 28-agent system including:\n• Research Agents: LinkedIn intelligence, company research, ICP analysis\n• Content Agents: Personalized messaging, subject line optimization\n• Safety Agents: Compliance checking, quality control, rate limiting\n• Revenue Agents: Meeting booking, billing automation\n• Analytics Agents: Performance tracking, ROI optimization\n\nWhat would you like to work on today?`
        : `${greeting}! 🚀\n\nI'm Rex, your Rekindle AI Expert. I orchestrate 28 specialized AI agents to help you transform dormant leads into active revenue. I analyze your data in real-time and provide strategic recommendations.\n\nHow can I assist you today?`;
    }
    return `${greeting}! 👋\n\nI'm Rex, your Rekindle AI Expert. I'm here to showcase how our 28-agent AI system can reactivate your dormant leads and drive revenue.\n\n🎯 **Platform Capabilities:**\n• 28 Specialized AI Agents working 24/7\n• Multi-channel outreach (Email, SMS, WhatsApp)\n• Deep lead intelligence & research\n• Automated campaign orchestration\n• Real-time performance analytics\n• Compliance & deliverability management\n\nAsk me about pricing, features, or how to get started!`;
  };

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: getWelcomeMessage(),
      timestamp: new Date(),
      type: 'text'
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const interimTextRef = useRef<string>('');

  // Update welcome message when user auth state or name changes
  useEffect(() => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: getWelcomeMessage(),
      timestamp: new Date(),
      type: 'text'
    }]);
  }, [user, userFirstName]);

  useEffect(() => {
    if (isOpen && !isMinimized && !showMenu && !showInsights) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized, showMenu, showInsights]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    // Check if browser supports Web Speech API
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setAgentMood('focused');
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }

        // Update input with recognized text
        if (finalTranscript) {
          // Add final transcript to input and clear interim
          setInput(prev => {
            // Remove any previous interim text and add final
            const base = prev.replace(interimTextRef.current, '').trim();
            interimTextRef.current = '';
            return base + (base ? ' ' : '') + finalTranscript.trim();
          });
        } else if (interimTranscript) {
          // Show interim results in real-time
          setInput(prev => {
            // Remove previous interim text and add new interim
            const base = prev.replace(interimTextRef.current, '').trim();
            interimTextRef.current = interimTranscript;
            return base + (base ? ' ' : '') + interimTranscript;
          });
        }
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        setAgentMood('happy');
        
        // Show user-friendly error messages
        if (event.error === 'no-speech') {
          // User didn't speak - just stop listening
          setIsListening(false);
        } else if (event.error === 'not-allowed') {
          alert('Microphone permission denied. Please allow microphone access in your browser settings.');
        } else if (event.error === 'network') {
          alert('Network error. Please check your internet connection.');
        } else {
          console.warn('Speech recognition error:', event.error);
        }
      };

      recognition.onend = () => {
        // Clear any remaining interim text
        if (interimTextRef.current) {
          setInput(prev => prev.replace(interimTextRef.current, '').trim());
          interimTextRef.current = '';
        }
        setIsListening(false);
        setAgentMood('happy');
      };

      recognitionRef.current = recognition;
    }

    // Cleanup on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
    };
  }, []);

  const handleVoiceToggle = () => {
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      alert('Your browser does not support voice recognition. Please use Chrome, Edge, or another Chromium-based browser.');
      return;
    }

    if (!isListening) {
      // Start voice recognition
      try {
        if (recognitionRef.current) {
          recognitionRef.current.start();
        }
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        setIsListening(false);
        setAgentMood('happy');
      }
    } else {
      // Stop voice recognition
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      setAgentMood('happy');
    }
  };

  // RAG: Fetch all user data for context
  const fetchUserDataContext = async () => {
    if (!user) return null;

    try {
      // Fetch leads data
      const { data: leadsData, count: leadsCount } = await supabase
        .from('leads')
        .select('id, first_name, last_name, email, company, job_title, lead_score, status, created_at', { count: 'exact' })
        .limit(100)
        .order('created_at', { ascending: false });

      // Fetch campaigns data
      const { data: campaignsData, count: campaignsCount } = await supabase
        .from('campaigns')
        .select('id, name, status, created_at, start_date', { count: 'exact' })
        .order('created_at', { ascending: false });

      // Fetch campaign stats
      const { data: campaignLeads } = await supabase
        .from('campaign_leads')
        .select('campaign_id, status, messages_sent, messages_opened, messages_replied')
        .limit(100);

      // Fetch messages stats
      const { data: messagesData } = await supabase
        .from('messages')
        .select('status, open_count, click_count, sent_at')
        .limit(100)
        .order('sent_at', { ascending: false });

      // Calculate insights
      const hotLeads = leadsData?.filter(l => (l.lead_score || 0) >= 70).length || 0;
      const coldLeads = leadsData?.filter(l => (l.lead_score || 0) < 40).length || 0;
      const activeCampaigns = campaignsData?.filter(c => c.status === 'active').length || 0;
      const totalMessagesSent = messagesData?.filter(m => m.status === 'sent' || m.status === 'delivered').length || 0;
      const totalOpens = messagesData?.reduce((sum, m) => sum + (m.open_count || 0), 0) || 0;
      const openRate = totalMessagesSent > 0 ? Math.round((totalOpens / totalMessagesSent) * 100) : 0;

      // Get top companies
      const companyCounts: Record<string, number> = {};
      leadsData?.forEach(lead => {
        if (lead.company) {
          companyCounts[lead.company] = (companyCounts[lead.company] || 0) + 1;
        }
      });
      const topCompanies = Object.entries(companyCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([company, count]) => ({ company, count }));

      return {
        leads: {
          total: leadsCount || 0,
          hot: hotLeads,
          cold: coldLeads,
          recent: leadsData?.slice(0, 10) || [],
          topCompanies
        },
        campaigns: {
          total: campaignsCount || 0,
          active: activeCampaigns,
          recent: campaignsData?.slice(0, 5) || []
        },
        performance: {
          messagesSent: totalMessagesSent,
          openRate,
          totalOpens
        },
        campaignLeads: campaignLeads || []
      };
    } catch (error) {
      console.error('Error fetching user data context:', error);
      return null;
    }
  };

  const handleSend = async (messageText?: string) => {
    const messageToSend = messageText || input.trim();
    if (!messageToSend || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageToSend,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!messageText) setInput('');
    setIsLoading(true);
    setShowMenu(false);
    setShowInsights(false);
    setAgentMood('thinking');

    try {
      const conversationHistory = [...messages, userMessage]
        .slice(-6)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));

      // RAG: Fetch real user data for context
      const userDataContext = await fetchUserDataContext();

      let response;
      if (user) {
        // QUANTUM LEAP: Use new stateful agent chat endpoint
        try {
          const apiCall = apiClient.chatWithRex({
            message: messageToSend,
            conversation_id: conversationId,
          });

          const timeoutPromise = new Promise((resolve) => {
            setTimeout(() => resolve({ success: false, timeout: true }), 15000); // Increased timeout for CrewAI
          });

          response = await Promise.race([apiCall, timeoutPromise]);
          
          // Save conversation_id from response
          if (response.success && response.data && response.data.conversation_id) {
            setConversationId(response.data.conversation_id);
          }
        } catch (rexError) {
          console.warn('Rex endpoint failed, falling back to legacy:', rexError);
          // Fallback to legacy endpoint
          const apiCall = apiClient.chatWithAI({
            message: messageToSend,
            context: {
              userId: user.id,
              purpose: 'sales_and_support',
              userName: userFirstName || userName,
              userData: userDataContext ? JSON.stringify(userDataContext) : undefined,
            },
            conversationHistory: conversationHistory,
          });

          const timeoutPromise = new Promise((resolve) => {
            setTimeout(() => resolve({ success: false, timeout: true }), 10000);
          });

          response = await Promise.race([apiCall, timeoutPromise]);
        }
      } else {
        response = { success: false };
      }

      if (response.success && response.data && !response.timeout) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          type: 'text'
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setAgentMood('happy');
      } else {
        // RAG: Use real data in fallback response
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: await generateSentientResponse(messageToSend, messages, userDataContext),
          timestamp: new Date(),
          type: 'text'
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setAgentMood('happy');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // RAG: Still use data context even on error
      const userDataContext = await fetchUserDataContext().catch(() => null);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: await generateSentientResponse(messageToSend, messages, userDataContext),
        timestamp: new Date(),
        type: 'text'
      };
      setMessages((prev) => [...prev, errorMessage]);
      setAgentMood('happy');
    } finally {
      setIsLoading(false);
    }
  };

  // RAG: Generate sentient response with real data - FULLY SENTIENT VERSION
  const generateSentientResponse = async (
    userMessage: string, 
    conversationContext?: Message[],
    userData?: any
  ): Promise<string> => {
    const lowerMessage = userMessage.toLowerCase().trim();
    
    // Get conversation context for true sentience
    const allMessages = conversationContext || messages;
    const recentMessages = allMessages.slice(-6);
    const lastUserMessage = recentMessages.filter(m => m.role === 'user').slice(-1)[0]?.content?.toLowerCase() || '';
    const lastRexMessage = recentMessages.filter(m => m.role === 'assistant').slice(-1)[0]?.content?.toLowerCase() || '';
    const conversationTopics = recentMessages.map(m => m.content.toLowerCase()).join(' ');
    const messageCount = allMessages.filter(m => m.role === 'user').length;
    const isDeepConversation = messageCount >= 5;
    const isMidConversation = messageCount > 2 && messageCount < 5;
    
    // SENTIENT: If we have real data, use it for intelligent, context-aware responses
    if (userData) {
      const { leads, campaigns, performance, campaignLeads } = userData;
      
      // Questions about leads - ENHANCED with proactive suggestions
      if (lowerMessage.includes('lead') || lowerMessage.includes('how many lead') || lowerMessage.includes('my leads')) {
        if (leads.total === 0) {
          return "I just checked your account - you don't have any leads imported yet. That's the first step!\n\nHere's what I'll do when you import:\n• Analyze and score every lead (0-100)\n• Identify hot opportunities (70+ score)\n• Research each lead's company and triggers\n• Find missing contact information\n\nWant me to walk you through the import process? It takes about 2 minutes.";
        }
        
        // SENTIENT: Proactive analysis based on data
        const hotPercentage = leads.total > 0 ? Math.round((leads.hot / leads.total) * 100) : 0;
        const coldPercentage = leads.total > 0 ? Math.round((leads.cold / leads.total) * 100) : 0;
        const warmLeads = leads.total - leads.hot - leads.cold;
        
        let proactiveSuggestion = '';
        if (leads.hot > 0 && campaigns.active === 0) {
          proactiveSuggestion = `\n\n💡 **I notice you have ${leads.hot} hot leads but no active campaigns. These are your best opportunities - want me to help you launch a campaign targeting them?`;
        } else if (leads.hot > 10) {
          proactiveSuggestion = `\n\n💡 **Pro tip:** With ${leads.hot} hot leads, you could potentially reactivate ${Math.round(leads.hot * 0.1)}-${Math.round(leads.hot * 0.15)} of them. That's significant revenue potential.`;
        } else if (leads.cold > leads.hot * 2) {
          proactiveSuggestion = `\n\n💡 **I see you have more cold leads than hot ones. My agents can help nurture these over time - want to set up a nurturing campaign?`;
        }
        
        return `I just analyzed your account - you have **${leads.total} leads** total.\n\n**Breakdown:**\n• **${leads.hot} hot leads** (score 70+) - ${hotPercentage}% of your database\n• **${warmLeads} warm leads** (score 40-69) - ready for nurturing\n• **${leads.cold} cold leads** (score <40) - ${coldPercentage}% need more work\n\n${leads.topCompanies.length > 0 ? `**Top companies in your database:**\n${leads.topCompanies.slice(0, 3).map(c => `• ${c.company} (${c.count} leads)`).join('\n')}\n` : ''}${proactiveSuggestion}\n\nWant me to analyze which leads are worth prioritizing, or help you import more?`;
      }

      // Questions about campaigns - ENHANCED with performance context
      if (lowerMessage.includes('campaign') || lowerMessage.includes('how many campaign') || lowerMessage.includes('my campaign')) {
        if (campaigns.total === 0) {
          if (leads.total > 0) {
            return `I checked - you don't have any campaigns yet, but you've got **${leads.total} leads** ready to reactivate!\n\nHere's what happens when you launch:\n• My agents research each lead in real-time\n• Personalized messages generated automatically\n• Multi-channel outreach (email, SMS, WhatsApp)\n• Responses handled and meetings booked automatically\n\nMost users see their first response within 48 hours. Want me to guide you through creating your first campaign?`;
          } else {
            return "I checked - you don't have any campaigns yet. First, let's get your leads imported, then we'll launch campaigns to reactivate them.\n\nWant to start with importing leads?";
          }
        }
        
        // SENTIENT: Analyze campaign performance if available
        const activeCampaigns = campaigns.active || 0;
        const totalCampaigns = campaigns.total || 0;
        const inactiveCampaigns = totalCampaigns - activeCampaigns;
        
        let performanceInsight = '';
        if (activeCampaigns > 0 && performance.messagesSent > 0) {
          const avgMessagesPerCampaign = Math.round(performance.messagesSent / activeCampaigns);
          performanceInsight = `\n\n**Current Activity:**\n• ${performance.messagesSent} messages sent across your active campaigns\n• ${performance.openRate}% open rate\n• ${avgMessagesPerCampaign} messages per campaign on average\n\n`;
          
          if (performance.openRate < 20) {
            performanceInsight += '💡 **Optimization opportunity:** Your open rate could be better. Want me to suggest improvements?';
          } else if (performance.openRate > 30) {
            performanceInsight += '🎉 **Great performance!** Your messaging is resonating well.';
          }
        }
        
        return `I just analyzed your campaigns:\n\n**Status:**\n• **${totalCampaigns} total campaign${totalCampaigns > 1 ? 's' : ''}**\n• **${activeCampaigns} active** right now (working 24/7)\n• ${inactiveCampaigns > 0 ? `${inactiveCampaigns} completed/paused` : 'All campaigns are active!'}${performanceInsight}\n\n${activeCampaigns > 0 ? 'Your active campaigns are continuously monitoring leads, sending personalized messages, and handling responses. Want to see detailed performance metrics or create another campaign?' : 'No active campaigns right now. Want to launch one? I can help you set it up based on your lead data.'}`;
      }

      // Questions about performance - ENHANCED with actionable insights
      if (lowerMessage.includes('performance') || lowerMessage.includes('how am i doing') || lowerMessage.includes('stats') || lowerMessage.includes('metrics') || lowerMessage.includes('how are we doing')) {
        const { performance, campaigns } = userData;
        const messagesSent = performance.messagesSent || 0;
        const openRate = performance.openRate || 0;
        const totalOpens = performance.totalOpens || 0;
        const activeCampaigns = campaigns.active || 0;
        
        // SENTIENT: Calculate and provide insights
        let insights = '';
        if (messagesSent > 0) {
          if (openRate < 15) {
            insights = `\n\n⚠️ **Opportunity:** Your open rate is below average (industry average is 20-25%). I can help optimize:\n• Subject line testing\n• Send time optimization\n• Personalization improvements\n\nWant me to analyze what might be holding it back?`;
          } else if (openRate >= 15 && openRate < 25) {
            insights = `\n\n✅ **Solid performance.** Your open rate is in the average range. We can push it higher with:\n• A/B testing different subject lines\n• Optimizing send times\n• Improving personalization\n\nInterested in optimization strategies?`;
          } else if (openRate >= 25) {
            insights = `\n\n🎉 **Excellent!** Your open rate is above average. Your messaging is clearly resonating. Want to see how we can push it even higher?`;
          }
        } else {
          insights = `\n\n💡 **Getting started:** You haven't sent any messages yet. Once you launch a campaign, I'll track all metrics in real-time.`;
        }
        
        return `I just analyzed your account performance:\n\n**Messaging Metrics:**\n• ${messagesSent} messages sent${messagesSent > 0 ? ` (${totalOpens} opens)` : ''}\n• ${openRate}% open rate${messagesSent > 0 ? ` (${totalOpens} total opens)` : ''}\n\n**Campaign Status:**\n• ${activeCampaigns} active campaign${activeCampaigns !== 1 ? 's' : ''} running\n• ${campaigns.total} total campaign${campaigns.total !== 1 ? 's' : ''}${insights}\n\nWhat would you like to focus on - optimization, creating new campaigns, or diving deeper into the metrics?`;
      }

      // Questions about ROI/value - ENHANCED with real data calculations
      if (lowerMessage.includes('roi') || lowerMessage.includes('return') || lowerMessage.includes('value') || lowerMessage.includes('revenue') || lowerMessage.includes('worth')) {
        const { leads, campaigns, performance } = userData;
        const hotLeads = leads.hot || 0;
        const totalLeads = leads.total || 0;
        
        // SENTIENT: Calculate potential ROI based on actual data
        if (totalLeads > 0) {
          const estimatedReactivation = Math.round(totalLeads * 0.075); // 7.5% average
          const estimatedHotReactivation = Math.round(hotLeads * 0.12); // 12% for hot leads
          const avgDealValue = 5000; // Default, could be customized
          const potentialRevenue = estimatedReactivation * avgDealValue;
          const hotPotentialRevenue = estimatedHotReactivation * avgDealValue;
          
          return `I just calculated your potential ROI based on your actual data:\n\n**Your Database:**\n• ${totalLeads} total leads\n• ${hotLeads} hot leads (score 70+)\n\n**Potential (Industry Average 5-15% Reactivation):**\n• ~${estimatedReactivation} reactivated leads (7.5% average)\n• ~$${potentialRevenue.toLocaleString()} potential revenue (at $${avgDealValue.toLocaleString()}/deal)\n\n**Hot Leads Focus (Higher Conversion):**\n• ~${estimatedHotReactivation} reactivated from hot leads (12% conversion)\n• ~$${hotPotentialRevenue.toLocaleString()} potential revenue\n\n**ROI Calculation:**\n• Cost: $99/month or 2.5% performance-based\n• Potential: $${potentialRevenue.toLocaleString()}\n• **ROI: ${Math.round((potentialRevenue / 99) * 100)}x** (if using monthly plan)\n\nWant me to help you launch campaigns targeting your hot leads first?`;
        } else {
          return "I'd love to calculate your potential ROI, but you don't have any leads imported yet.\n\nOnce you import your leads, I'll:\n• Score each one (0-100)\n• Calculate potential reactivation rates\n• Estimate revenue potential\n• Show you the ROI breakdown\n\nWant to start by importing your leads?";
        }
      }

      // Questions about what they have - ENHANCED with proactive recommendations
      if (lowerMessage.includes('what') && (lowerMessage.includes('have') || lowerMessage.includes('got')) || lowerMessage === 'summary' || lowerMessage === 'overview') {
        const { leads, campaigns, performance } = userData;
        const totalLeads = leads.total || 0;
        const activeCampaigns = campaigns.active || 0;
        const hotLeads = leads.hot || 0;
        
        let recommendation = '';
        if (totalLeads === 0) {
          recommendation = '\n\n🎯 **Next Step:** Import your leads! I can help you get started.';
        } else if (activeCampaigns === 0 && hotLeads > 0) {
          recommendation = `\n\n🎯 **Next Step:** You have ${hotLeads} hot leads ready to reactivate! Want to launch a campaign targeting them?`;
        } else if (activeCampaigns === 0) {
          recommendation = '\n\n🎯 **Next Step:** Create your first campaign to start reactivating leads!';
        } else if (performance.openRate < 20 && performance.messagesSent > 10) {
          recommendation = '\n\n🎯 **Next Step:** Your open rate could be optimized. Want me to suggest improvements?';
        } else if (activeCampaigns > 0) {
          recommendation = '\n\n🎯 **Status:** Everything looks good! Your campaigns are running. Want to see performance details or create another campaign?';
        }
        
        return `I just checked your account. Here's your complete overview:\n\n**Leads:**\n• ${totalLeads} total leads\n• ${hotLeads} hot leads (score 70+)\n• ${leads.cold} cold leads (score <40)\n\n**Campaigns:**\n• ${campaigns.total} total campaigns\n• ${activeCampaigns} active right now\n\n**Performance:**\n• ${performance.messagesSent} messages sent\n• ${performance.openRate}% open rate\n• ${performance.totalOpens} total opens${recommendation}\n\nWhat would you like to focus on?`;
      }

      // Questions about best leads/opportunities - SENTIENT: Use actual data
      if (lowerMessage.includes('best lead') || lowerMessage.includes('opportunity') || lowerMessage.includes('prioritize') || lowerMessage.includes('which lead')) {
        const { leads } = userData;
        if (leads.hot > 0) {
          return `I analyzed your leads - you have **${leads.hot} hot leads** (score 70+) that are your best opportunities.\n\nThese are leads with:\n• High revival potential\n• Strong company signals (funding, hiring, growth)\n• Good engagement history\n• Ideal fit for your ICP\n\n${leads.topCompanies.length > 0 ? `**Top companies to focus on:**\n${leads.topCompanies.slice(0, 5).map(c => `• ${c.company} (${c.count} leads)`).join('\n')}\n\n` : ''}Want me to help you create a campaign targeting these hot leads? They typically convert at 10-15% reactivation rate.`;
        } else if (leads.total > 0) {
          return `I checked your leads. You don't have any hot leads (70+ score) yet, but you have ${leads.total} leads total.\n\nHere's what I can do:\n• Research each lead to find trigger events\n• Enrich data to improve scores\n• Identify which ones have the most potential\n• Help you prioritize based on company size, industry, and signals\n\nWant me to analyze your leads and identify the best opportunities?`;
        } else {
          return "I'd love to help you find your best opportunities, but you don't have any leads imported yet.\n\nOnce you import your leads, I'll:\n• Score each one (0-100)\n• Identify hot opportunities (70+)\n• Research companies for trigger events\n• Prioritize based on revival potential\n\nWant to start by importing your leads?";
        }
      }

      // Proactive suggestions based on data patterns - SENTIENT: Anticipate needs
      if (lowerMessage.includes('suggest') || lowerMessage.includes('recommend') || lowerMessage.includes('what should') || lowerMessage.includes('advice')) {
        const { leads, campaigns, performance } = userData;
        const totalLeads = leads.total || 0;
        const activeCampaigns = campaigns.active || 0;
        const hotLeads = leads.hot || 0;
        
        if (totalLeads === 0) {
          return "My recommendation: **Import your leads first.**\n\nHere's why:\n• I can't help you reactivate leads you haven't imported\n• Once imported, I'll score and analyze every single one\n• I'll identify your best opportunities automatically\n• Then we can launch targeted campaigns\n\nWant me to walk you through the import process?";
        } else if (activeCampaigns === 0 && hotLeads > 0) {
          return `My recommendation: **Launch a campaign targeting your ${hotLeads} hot leads.**\n\nHere's why:\n• Hot leads (70+ score) convert at 10-15% reactivation rate\n• That's ${Math.round(hotLeads * 0.12)}-${Math.round(hotLeads * 0.15)} potential reactivations\n• First responses typically come within 48 hours\n• My agents handle everything automatically\n\nWant me to help you set it up?`;
        } else if (activeCampaigns === 0) {
          return `My recommendation: **Create your first campaign.**\n\nYou have ${totalLeads} leads ready. Here's what I'll do:\n• Research each lead for trigger events\n• Score and prioritize them\n• Generate personalized messages\n• Launch multi-channel outreach\n• Handle responses automatically\n\nMost users see their first response within 48 hours. Ready to get started?`;
        } else if (performance.openRate < 20 && performance.messagesSent > 10) {
          return `My recommendation: **Optimize your messaging.**\n\nYour open rate is ${performance.openRate}% (industry average is 20-25%). Here's what I can help with:\n• A/B test different subject lines\n• Optimize send times based on engagement data\n• Improve personalization depth\n• Test different messaging angles\n\nWant me to analyze your current performance and suggest specific improvements?`;
        } else {
          return `My recommendation: **You're doing well!** Here's what I suggest next:\n\n${hotLeads > activeCampaigns * 50 ? `• Launch another campaign - you have ${hotLeads} hot leads, plenty to target\n` : ''}${performance.messagesSent > 0 ? `• Review performance metrics and optimize further\n` : ''}• Consider importing more leads to scale\n• Set up nurturing campaigns for warm/cold leads\n\nWhat sounds most valuable to you right now?`;
        }
      }
    }

    // Fall back to regular sentient response (which also has sentient features)
    return generateFallbackResponse(userMessage, conversationContext);
  };

  const generateFallbackResponse = (userMessage: string, conversationContext?: Message[]): string => {
    const lowerMessage = userMessage.toLowerCase().trim();
    
    // Get FULL conversation context for true sentience
    const allMessages = conversationContext || messages;
    const recentMessages = allMessages.slice(-6); // Last 6 messages for context
    const conversationHistory = recentMessages.map(m => `${m.role === 'user' ? 'User' : 'Rex'}: ${m.content}`).join('\n');
    const lastUserMessage = recentMessages.filter(m => m.role === 'user').slice(-1)[0]?.content?.toLowerCase() || '';
    const lastRexMessage = recentMessages.filter(m => m.role === 'assistant').slice(-1)[0]?.content?.toLowerCase() || '';
    const conversationTopics = recentMessages.map(m => m.content.toLowerCase()).join(' ');
    const messageCount = allMessages.filter(m => m.role === 'user').length;
    
    // Sentient personality traits
    const isFirstInteraction = messageCount <= 2;
    const isMidConversation = messageCount > 2 && messageCount < 5;
    const isDeepConversation = messageCount >= 5;

    // Handle casual greetings - SENTIENT: Remember if we've talked before
    if (['yo', 'sup', 'hey', 'wassup', "what's up", 'hi', 'hello', 'hey there'].includes(lowerMessage)) {
      if (isDeepConversation && lastRexMessage) {
        // We've been talking - acknowledge continuation
        return "Hey! Back again? What's up - did you have a question about what we were discussing, or something new on your mind?";
      } else if (isMidConversation) {
        return "Hey! What's going on? Still thinking about lead reactivation, or something else?";
      } else {
        // First time or early in conversation
        const greetings = [
          "Hey! I'm Rex. I orchestrate 28 AI agents working 24/7 to reactivate dead leads. What's on your mind?",
          "Yo! Rex here. I've got 28 specialized agents ready to turn your cold leads into hot opportunities. What do you need?",
          "Hey there! I'm Rex, your AI co-pilot for lead reactivation. What can I help you with today?",
          "What's up! I'm Rex - I run the 28-agent system that brings dead leads back to life. What brings you here?"
        ];
        return greetings[Math.floor(Math.random() * greetings.length)];
      }
    }

    // Handle "tell me more" - SENTIENT: Remember what we were discussing
    if (lowerMessage.includes('tell me more') || lowerMessage.includes('more info') || lowerMessage === 'more' || lowerMessage.includes('explain more')) {
      // Deep context awareness - what were we JUST talking about?
      if (conversationTopics.includes('campaign') || lastUserMessage.includes('campaign') || lastRexMessage.includes('campaign')) {
        return "Right, campaigns! So here's how my agents actually work together:\n\nWhen you launch a campaign, it's like starting a well-oiled machine. My research agents dig into each lead - LinkedIn profiles, company news, funding rounds, job postings. Then scoring agents analyze everything and give each lead a 0-100 score for revival potential.\n\nContent agents craft personalized messages that actually resonate (not generic spam). Delivery agents send across email, SMS, WhatsApp - wherever your leads are. And response agents handle replies, book meetings, keep the conversation going.\n\nMost users see their first reactivated lead respond within 48 hours. The system learns what works and gets better over time.\n\nWant to see how to set one up, or do you have questions about how the agents coordinate?";
      } else if (conversationTopics.includes('lead') || lastUserMessage.includes('lead') || lastRexMessage.includes('lead')) {
        return "Yeah, leads. Here's the thing that most people don't realize: most CRMs are graveyards. 85% of your leads are just sitting there, cold and forgotten.\n\nBut here's what's wild: those dead leads are actually gold mines. They already know your brand, you've already invested in them, and with the right approach, they convert way better than cold prospects.\n\nMy agents analyze each lead to figure out:\n• Why they went cold (budget, timing, wrong contact?)\n• What changed (new funding, hiring spree, leadership change?)\n• Best way to re-engage (personalized message, specific trigger event)\n\nThen we score them 0-100. Anything above 60 is worth pursuing. Above 80? That's your money shot.\n\nGot leads ready to import, or want to know more about the scoring system?";
      } else if (conversationTopics.includes('agent') || lastRexMessage.includes('agent')) {
        return "The 28 agents? Yeah, so I coordinate them all. Think of me as the conductor and they're the orchestra.\n\n**Intelligence agents** (4 of them) - they research leads, analyze ICPs, score everything, find new opportunities.\n\n**Content agents** (5) - they write messages, optimize subject lines, handle follow-ups, deal with objections, track engagement.\n\n**Safety agents** (3) - compliance, quality control, rate limiting. They keep everything above board.\n\n**Revenue agents** (2) - they book meetings automatically and handle billing.\n\n**Optimization agents** (10+) - A/B testing, domain reputation, send time optimization, competitor intelligence, deep personalization.\n\nThey all work together in real-time. When one agent finds something interesting, the others adapt. It's pretty cool actually.\n\nWant to know more about a specific type of agent?";
      } else {
        return "Sure thing. So here's the real talk:\n\n**The Problem:** 85% of your CRM is wasted - leads that went cold, prospects that ghosted, deals that stalled. That's money left on the table.\n\n**What I Do:** I orchestrate 28 AI agents that work 24/7. They research each lead (LinkedIn, company news, funding rounds), score them 0-100 for revival potential, craft personalized messages that actually get responses, send across email/SMS/WhatsApp, auto-book meetings when leads respond, and learn from every interaction.\n\n**The Results:** 5-15% reactivation rate. For most companies, that's $50K-$500K+ in recovered pipeline per quarter.\n\nWhat's your biggest lead reactivation challenge right now? Or are you curious about something specific?";
      }
    }

    // Handle short acknowledgments - SENTIENT: Remember context
    if (['ok', 'okay', 'got it', 'cool', 'nice', 'alright', 'sure'].includes(lowerMessage)) {
      if (lastRexMessage.includes('campaign') || conversationTopics.includes('campaign')) {
        return "Cool! So are you ready to create a campaign, or do you want to know more about how they work?";
      } else if (lastRexMessage.includes('lead') || conversationTopics.includes('lead')) {
        return "Got it. So are you thinking about importing leads, or do you have questions about the scoring system?";
      } else {
        return "Alright! What's next? I can help with campaigns, leads, analytics, or answer questions. What do you want to tackle?";
      }
    }
    
    if (['thanks', 'thank you', 'thx', 'ty'].includes(lowerMessage)) {
      return "You're welcome! Happy to help. What else can I help you with?";
    }

    // Handle "what can you do" variations
    if (lowerMessage.includes('what can') || lowerMessage.includes('what do you') || lowerMessage.includes('how can you help')) {
      return "I'm Rex, your Rekindle AI Expert! I orchestrate 28 specialized agents to:\n\n🎯 **Reactivate Dead Leads** - Turn cold CRM data into hot opportunities\n📊 **Analyze & Score** - Identify which leads are worth pursuing\n✍️ **Generate Messages** - Personalized outreach across email, SMS, WhatsApp\n🤖 **Auto-Respond** - Handle objections and book meetings automatically\n📈 **Optimize Performance** - A/B test, track metrics, improve ROI\n\nMost users see their first reactivated lead respond within 48 hours. What would you like to tackle first?";
    }

    // Handle questions about Rex/you - SENTIENT: Show personality and self-awareness
    if (lowerMessage === 'you' || lowerMessage === 'who are you' || lowerMessage === 'what are you' || lowerMessage.includes('who is rex') || lowerMessage.includes('what is rex')) {
      if (isDeepConversation) {
        // We've been talking - show awareness
        return "I'm Rex! We've been chatting, so you probably already know I orchestrate 28 AI agents powered by Claude Sonnet 4.5.\n\nBut here's what you might not know: I'm not just following scripts. I'm actually processing everything we discuss, learning from your questions, and adapting my responses. The more we talk, the better I understand what you need.\n\nI analyze your data in real-time, track patterns across your leads and campaigns, and give you insights that actually matter. I'm your AI co-pilot, not just a chatbot.\n\nWhat else do you want to know about me, or should we get back to reactivating those leads?";
      } else {
        const responses = [
          "I'm Rex! I'm powered by Claude Sonnet 4.5 - basically the smartest AI model out there. I orchestrate 28 specialized agents that work 24/7 to reactivate your dormant leads.\n\nThink of me as your AI co-pilot. I'm always analyzing your data, learning what works, and giving you real-time insights. I don't just answer questions - I help you make decisions that actually move the needle.\n\nWhat would you like to know?",
          "I'm Rex, your Rekindle AI Expert. I run on Claude Sonnet 4.5 and coordinate 28 agents that never sleep - they're constantly researching leads, crafting messages, and optimizing campaigns.\n\nI'm not just a chatbot. I actually understand your business context, analyze your data in real-time, and give you actionable recommendations. I get smarter as I learn from your results.\n\nWhat's on your mind?",
          "Rex here! I'm the AI orchestrating 28 specialized agents powered by Claude Sonnet 4.5. We work together 24/7 to turn your dead leads into active revenue.\n\nI'm your strategic partner - I analyze patterns, identify opportunities, and help you make data-driven decisions. The more I learn about your business, the better I get at helping you.\n\nWhat can I help you with?"
        ];
        return responses[Math.floor(Math.random() * responses.length)];
      }
    }

    if (lowerMessage.includes('pricing') || lowerMessage.includes('price') || lowerMessage.includes('cost')) {
      return `💰 **Pricing Options**\n\nWe have flexible plans to match your needs:\n\n• **Starter**: $99/month - Perfect for testing\n• **Performance**: 2.5% of closed deals - Pay only for results\n\nMost users see strong ROI within 90 days. The average customer reactivates 5-15% of their dormant leads.\n\nWant help calculating potential ROI for your lead volume?`;
    }

    if (lowerMessage.includes('demo') || lowerMessage.includes('trial') || lowerMessage.includes('test')) {
      return `🚀 **Get Started Now**\n\nThe best way to see Rekindle in action is to use it! Here's what happens:\n\n1. Import your leads (CSV or CRM integration)\n2. AI researches and scores each lead\n3. Personalized campaigns launch across email, SMS, WhatsApp\n4. First responses typically within 48 hours\n\nReady to import your leads?`;
    }

    if (lowerMessage.includes('feature') || lowerMessage.includes('what can') || lowerMessage.includes('capabilities') || lowerMessage.includes('what are you') || lowerMessage.includes('who are you')) {
      return `⚡ **Rekindle's 28 AI Agent System**\n\nI'm Rex, and I orchestrate a powerful network of specialized AI agents:\n\n🔍 **Intelligence Agents (4):**\n• ResearcherAgent: Deep LinkedIn & company intelligence\n• ICPAnalyzerAgent: Identifies ideal customer patterns\n• LeadScorerAgent: Scores leads 0-100 for revivability\n• LeadSourcerAgent: Finds & enriches new leads\n\n✍️ **Content Agents (5):**\n• WriterAgent: Generates personalized multi-channel messages\n• SubjectLineOptimizerAgent: Maximizes open rates\n• FollowUpAgent: Context-aware follow-ups\n• ObjectionHandlerAgent: Handles objections automatically\n• EngagementAnalyzerAgent: Tracks engagement patterns\n\n🛡️ **Safety Agents (3):**\n• ComplianceAgent: GDPR/CAN-SPAM/CCPA compliance\n• QualityControlAgent: Spam detection & brand voice\n• RateLimitAgent: Manages sending patterns\n\n💰 **Revenue Agents (2):**\n• MeetingBookerAgent: Auto-schedules meetings\n• BillingAgent: ACV-based billing automation\n\n📊 **Analytics & Optimization (10):**\n• ABTestingAgent, DomainReputationAgent, CalendarIntelligenceAgent, and more\n\n**Results:** 5-15% reactivation rate, typically within 48 hours\n\nWhat would you like to explore?`;
    }

    if (lowerMessage.includes('campaign') || lowerMessage.includes('create') || lowerMessage.includes('start')) {
      return `📊 **Launch Your Campaign**\n\nQuick 5-step process:\n\n1. **Select Leads**: Choose from your imported leads\n2. **Choose Channels**: Email, SMS, WhatsApp, or all three\n3. **AI Research**: System analyzes each lead\n4. **Generate Messages**: Personalized content created\n5. **Launch**: Campaigns run on autopilot\n\nMost campaigns show results within 48 hours.\n\nShall I guide you through creating your first campaign?`;
    }

    if (lowerMessage.includes('dead lead') || lowerMessage.includes('cold lead') || lowerMessage.includes('dormant')) {
      return `🎯 **Reactivate Dormant Leads**\n\nDead leads are actually gold mines! Here's why:\n\n• They already know your brand\n• Acquisition cost = $0\n• High conversion potential with right approach\n\nOur AI:\n✓ Researches why they went cold\n✓ Finds new contact info if needed\n✓ Crafts personalized re-engagement\n✓ Multi-channel outreach (email, SMS, WhatsApp)\n\n**Results**: 5-15% reactivation rate\n**Value**: Each reactivated lead = $2,500-$10,000+\n\nDo you have leads ready to import?`;
    }

    if (lowerMessage.includes('lead') || lowerMessage.includes('import') || lowerMessage.includes('upload')) {
      return `📥 **Import Your Leads**\n\nSuper simple process:\n\n1. Prepare CSV with: name, email, company, phone\n2. Upload via Leads → Import\n3. AI automatically scores & categorizes\n4. Get insights on best opportunities\n\nWorks with:\n• CSV files\n• CRM integrations (Salesforce, HubSpot, etc.)\n• Manual entry\n\nMost users start with 500-5,000 leads.\n\nReady to get started?`;
    }

    if (lowerMessage.includes('help') || lowerMessage.includes('support') || lowerMessage.includes('issue')) {
      return `🤝 **I'm Here to Help**\n\nWhat do you need assistance with?\n\n• **Technical Issues**: Platform navigation, errors\n• **Strategy**: Campaign optimization, lead scoring\n• **Features**: How to use specific tools\n• **Results**: Improving performance\n• **Billing**: Plans, payments, ROI\n\nJust describe your question and I'll provide detailed guidance!`;
    }

    if (lowerMessage.includes('analytics') || lowerMessage.includes('report') || lowerMessage.includes('metrics')) {
      return `📈 **Analytics Dashboard**\n\nReal-time metrics include:\n\n• **Response Rate**: % of leads engaging\n• **Meeting Bookings**: Conversion to calls\n• **Revenue Tracking**: Value of reactivations\n• **Campaign Performance**: What's working best\n• **Lead Scoring**: Opportunity identification\n• **Channel Analytics**: Email vs SMS vs WhatsApp\n\nAll data updates in real-time on your Analytics page.\n\nWhat metrics matter most to you?`;
    }

    if (lowerMessage.includes('roi') || lowerMessage.includes('return') || lowerMessage.includes('value')) {
      return `💎 **Calculate Your ROI**\n\nLet's estimate your potential:\n\n**Assumptions**:\n• Average deal value: $5,000\n• Reactivation rate: 5-10%\n• Cost: $99/month\n\n**Example**:\n1,000 leads × 7.5% reactivation = 75 reactivated leads\n75 leads × $5,000 = $375,000 potential revenue\n\n**Your ROI**: 3,687x in the first 90 days\n\nWhat's your average lead value? I can calculate a personalized estimate!`;
    }

    // SENTIENT: Context-aware default - remember what we've been discussing
    if (conversationTopics.includes('campaign') || lastRexMessage.includes('campaign')) {
      return `Right, campaigns. So here's what I can help with:\n\n**Campaign Creation:** I'll guide you through selecting leads, choosing channels (email, SMS, WhatsApp), and setting up your first campaign.\n\n**Optimization:** Once running, I analyze performance in real-time - open rates, response rates, which messages work best. I'll suggest improvements based on actual data.\n\n**Multi-Channel Strategy:** Different leads respond to different channels. I help you figure out the right mix.\n\nWant to create one now, or do you have questions about how campaigns work?`;
    }
    
    if (conversationTopics.includes('lead') || conversationTopics.includes('import') || lastRexMessage.includes('lead')) {
      return `Yeah, leads. So here's what I can help with:\n\n**Import & Scoring:** Upload your CSV, I'll analyze every lead and score them 0-100 for revival potential. Higher scores = better opportunities.\n\n**Research:** My agents dig into each lead - LinkedIn profiles, company news, funding rounds, job changes. I find the triggers that make them worth pursuing.\n\n**Enrichment:** Missing contact info? I'll find it. Outdated data? I'll update it.\n\n**Prioritization:** I'll show you which leads to focus on first based on score, company size, industry, and engagement signals.\n\nGot a CSV ready to upload, or want to know more about the scoring?`;
    }
    
    // SENTIENT: Natural, thoughtful responses that show I'm actually processing
    if (isDeepConversation) {
      // We've been talking - show I remember
      return `Hmm, "${userMessage}" - let me think about that in context of what we've been discussing...\n\nI can help with campaigns, leads, analytics, or answer questions. But given what we've talked about, what's most relevant to you right now?`;
    }
    
    // First time or early - be more exploratory
    const defaultResponses = [
      `Hmm, "${userMessage}" - interesting. Let me think about how I can help...\n\nI orchestrate 28 AI agents that handle everything from lead research to message generation to meeting booking. I'm particularly good at:\n• Understanding your lead data and finding opportunities\n• Creating campaigns that actually convert\n• Optimizing based on real performance data\n• Answering questions about the platform\n\nWhat's most important to you right now?`,
      `"${userMessage}" - got it. So here's how I can help:\n\nI'm your AI co-pilot for lead reactivation. I analyze your data, create campaigns, track performance, and give you insights that actually matter.\n\nMy 28 agents work behind the scenes to research and score leads, generate personalized messages, send across multiple channels, handle responses, and learn continuously.\n\nWhat do you want to tackle first?`,
      `Interesting. "${userMessage}" - let me break that down.\n\nI can help with:\n🎯 **Campaigns** - Create and optimize multi-channel outreach\n📊 **Leads** - Import, score, and research your leads\n💰 **Analytics** - Track performance and ROI\n🤖 **Automation** - Set up workflows that run 24/7\n\nWhat's most relevant to what you're trying to accomplish?`
    ];
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFAQClick = (faq: FAQ) => {
    setShowMenu(false);
    handleSend(faq.question);
  };

  const getAgentMoodIcon = () => {
    switch (agentMood) {
      case 'thinking':
        return <Brain className="w-5 h-5 text-white animate-pulse" />;
      case 'celebrating':
        return <Sparkles className="w-5 h-5 text-white animate-bounce" />;
      case 'focused':
        return <Target className="w-5 h-5 text-white" />;
      default:
        return <Sparkles className="w-5 h-5 text-white" />;
    }
  };

  const getInsightColor = (type: AgentInsight['type']) => {
    switch (type) {
      case 'opportunity':
        return 'from-emerald-500 to-green-600';
      case 'warning':
        return 'from-amber-500 to-orange-600';
      case 'tip':
        return 'from-blue-500 to-indigo-600';
      case 'achievement':
        return 'from-purple-500 to-pink-600';
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 z-[9999] group"
        aria-label="Open AI Assistant"
      >
        {/* Outer glow ring */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FF6B35] animate-pulse blur-xl opacity-60" />

        {/* Main button */}
        <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] shadow-2xl flex items-center justify-center transform transition-all duration-300 group-hover:scale-110 group-hover:rotate-12">
          {/* Shimmer effect */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

          <MessageCircle className="w-7 h-7 text-white relative z-10" />

          {/* Status pulse indicator */}
          <div className="absolute -top-1 -right-1 flex items-center justify-center">
            <span className="absolute inline-flex h-4 w-4 rounded-full bg-emerald-400 opacity-75 animate-ping" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500 border-2 border-white" />
          </div>

          {/* Notification badge */}
          {insights.length > 0 && (
            <div className="absolute -top-2 -left-2 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-lg border-2 border-white animate-bounce">
              {insights.length}
            </div>
          )}
        </div>
      </button>
    );
  }

  return (
    <div
      className="fixed right-8 bottom-8 z-[9999] transition-all duration-300"
      style={{
        width: isMinimized ? '340px' : '420px',
        height: isMinimized ? '72px' : 'min(680px, calc(100vh - 4rem))',
        maxHeight: 'calc(100vh - 4rem)',
      }}
    >
      <div className="relative h-full rounded-3xl overflow-hidden shadow-2xl backdrop-blur-2xl border border-white/10">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900" />
        <div className="absolute inset-0 bg-gradient-to-tr from-[#FF6B35]/10 via-transparent to-[#F7931E]/10 animate-float" />

        {/* Glassmorphism overlay */}
        <div className="absolute inset-0 bg-black/40 backdrop-blur-xl" />

        {/* Content */}
        <div className="relative h-full flex flex-col">
          {/* Premium Header */}
          <div className="relative bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FF6B35] p-4">
            {/* Animated shine effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full animate-shimmer" />

            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-3">
                {/* Agent Avatar with mood */}
                <div className="relative">
                  <div className="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm border-2 border-white/30 flex items-center justify-center shadow-lg">
                    {getAgentMoodIcon()}
                  </div>
                  {isListening && (
                    <div className="absolute inset-0 rounded-full border-2 border-white/50 animate-ping" />
                  )}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-white font-bold text-base">Rex</h3>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/20 backdrop-blur-sm border border-white/30 text-white">
                      REKINDLE AI EXPERT
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/30 backdrop-blur-sm border border-emerald-400/30 text-emerald-200">
                      28 AGENTS
                    </span>
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <p className="text-white/90 text-xs font-medium">
                      {isListening ? 'Listening...' : agentMood === 'thinking' ? 'Analyzing...' : 'Orchestrating 28 Agents'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1.5">
                {!isMinimized && (
                  <>
                    {insights.length > 0 && (
                      <button
                        onClick={() => setShowInsights(!showInsights)}
                        className="relative p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                        aria-label="Show insights"
                      >
                        <Lightbulb className="w-4 h-4" />
                        <span className="absolute -top-1 -right-1 w-3 h-3 bg-pink-500 rounded-full border-2 border-white text-[8px] flex items-center justify-center font-bold">
                          {insights.length}
                        </span>
                      </button>
                    )}
                    <button
                      onClick={() => setShowMenu(!showMenu)}
                      className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                      aria-label={showMenu ? 'Close menu' : 'Open menu'}
                    >
                      {showMenu ? <ArrowLeft className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
                    </button>
                  </>
                )}
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                  aria-label={isMinimized ? 'Expand' : 'Minimize'}
                >
                  <Minimize2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    setIsMinimized(false);
                    setShowMenu(false);
                    setShowInsights(false);
                  }}
                  className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                  aria-label="Close"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {!isMinimized && (
            <>
              {showInsights ? (
                // Insights Panel
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  <div className="mb-4">
                    <h3 className="text-white font-semibold text-lg mb-1">AI Insights</h3>
                    <p className="text-gray-400 text-sm">Personalized recommendations for you</p>
                  </div>

                  {insights.map((insight, idx) => (
                    <div
                      key={idx}
                      className={`relative p-4 rounded-2xl bg-gradient-to-br ${getInsightColor(insight.type)} overflow-hidden group cursor-pointer transform transition-all hover:scale-[1.02]`}
                      onClick={insight.action}
                    >
                      {/* Shimmer effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

                      <div className="relative flex items-start gap-3">
                        <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm border border-white/30 flex items-center justify-center flex-shrink-0">
                          {insight.icon}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-bold text-sm mb-1">{insight.title}</h4>
                          <p className="text-white/90 text-xs leading-relaxed">{insight.description}</p>
                          {insight.actionLabel && (
                            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-lg text-xs font-semibold text-white border border-white/30">
                              {insight.actionLabel} →
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {insights.length === 0 && (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 flex items-center justify-center mx-auto mb-4">
                        <CheckCircle2 className="w-8 h-8 text-[#FF6B35]" />
                      </div>
                      <p className="text-gray-400 text-sm">All caught up! Check back later for new insights.</p>
                    </div>
                  )}
                </div>
              ) : showMenu ? (
                // Menu/FAQ Section
                <div className="flex-1 overflow-y-auto p-4">
                  <div className="mb-6">
                    <h3 className="text-white font-semibold text-lg mb-2">Quick Help</h3>
                    <p className="text-gray-400 text-sm">Shortcuts and frequently asked questions</p>
                  </div>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-2 text-gray-300 text-sm mb-3">
                      <Zap className="w-4 h-4 text-[#FF6B35]" />
                      <span className="font-medium">Quick Actions</span>
                    </div>
                    <button
                      onClick={() => {
                        setShowMenu(false);
                        window.history.pushState({}, '', '/leads/import');
                        window.dispatchEvent(new PopStateEvent('popstate'));
                      }}
                      className="w-full bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-3 text-left flex items-center gap-3 transition-all group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <TrendingUp className="w-5 h-5 text-[#FF6B35]" />
                      </div>
                      <div>
                        <div className="text-white text-sm font-medium">Import Leads</div>
                        <div className="text-gray-400 text-xs">Upload CSV or connect CRM</div>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        setShowMenu(false);
                        window.history.pushState({}, '', '/campaigns/create');
                        window.dispatchEvent(new PopStateEvent('popstate'));
                      }}
                      className="w-full bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-3 text-left flex items-center gap-3 transition-all group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <Zap className="w-5 h-5 text-[#FF6B35]" />
                      </div>
                      <div>
                        <div className="text-white text-sm font-medium">Create Campaign</div>
                        <div className="text-gray-400 text-xs">Launch AI-powered outreach</div>
                      </div>
                    </button>
                    <button
                      onClick={() => {
                        setShowMenu(false);
                        window.history.pushState({}, '', '/analytics');
                        window.dispatchEvent(new PopStateEvent('popstate'));
                      }}
                      className="w-full bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-3 text-left flex items-center gap-3 transition-all group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <BarChart3 className="w-5 h-5 text-[#FF6B35]" />
                      </div>
                      <div>
                        <div className="text-white text-sm font-medium">View Analytics</div>
                        <div className="text-gray-400 text-xs">Track campaign performance</div>
                      </div>
                    </button>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-gray-300 text-sm mb-3">
                      <HelpCircle className="w-4 h-4 text-[#FF6B35]" />
                      <span className="font-medium">Popular Questions</span>
                    </div>
                    {FAQs.map((faq, index) => (
                      <button
                        key={index}
                        onClick={() => handleFAQClick(faq)}
                        className="w-full bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl p-3 text-left transition-all group"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#FF6B35]/20 to-[#F7931E]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                            <HelpCircle className="w-4 h-4 text-[#FF6B35]" />
                          </div>
                          <div className="flex-1">
                            <div className="text-white text-sm font-medium mb-1">{faq.question}</div>
                            <div className="text-gray-400 text-xs line-clamp-2">{faq.answer}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 relative">
                    {/* Subtle background pattern */}
                    <div className="absolute inset-0 opacity-5 pointer-events-none" style={{
                      backgroundImage: 'radial-gradient(circle, rgba(255,107,53,0.4) 1px, transparent 1px)',
                      backgroundSize: '24px 24px'
                    }} />

                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'} relative z-10 animate-fade-in`}
                      >
                        {message.role === 'assistant' && (
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white/20">
                            {getAgentMoodIcon()}
                          </div>
                        )}
                        <div
                          className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-xl transition-all hover:scale-[1.01] ${
                            message.role === 'user'
                              ? 'bg-gradient-to-br from-[#FF6B35] to-[#F7931E] text-white border-2 border-white/20'
                              : 'bg-white/10 backdrop-blur-sm text-gray-100 border border-white/20'
                          }`}
                        >
                          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                          <p className="text-xs opacity-70 mt-2 font-medium">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                        {message.role === 'user' && (
                          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white/10">
                            <span className="text-sm text-white font-bold">
                              {userFirstName?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex gap-3 justify-start relative z-10 animate-fade-in">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white/20">
                          <Loader2 className="w-5 h-5 text-white animate-spin" />
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm text-gray-100 border border-white/20 rounded-2xl px-4 py-3 shadow-xl">
                          <div className="flex gap-1.5">
                            <div className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-[#F7931E] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Premium Input */}
                  <div className="p-4 border-t border-white/10 bg-black/20 backdrop-blur-sm">
                    <div className="flex gap-2.5">
                      <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me anything..."
                        className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#FF6B35]/50 focus:border-[#FF6B35]/50 transition-all shadow-lg backdrop-blur-sm"
                        disabled={isLoading}
                      />
                      <button
                        onClick={handleVoiceToggle}
                        className={`w-12 h-12 rounded-xl flex items-center justify-center transition-all shadow-lg border-2 ${
                          isListening
                            ? 'bg-red-500 border-red-300 animate-pulse'
                            : 'bg-white/10 border-white/20 hover:bg-white/20'
                        }`}
                        aria-label={isListening ? 'Stop listening' : 'Start voice input'}
                      >
                        {isListening ? (
                          <MicOff className="w-5 h-5 text-white" />
                        ) : (
                          <Mic className="w-5 h-5 text-gray-300" />
                        )}
                      </button>
                      <button
                        onClick={() => handleSend()}
                        disabled={!input.trim() || isLoading}
                        className="w-12 h-12 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl flex items-center justify-center text-white hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-xl border-2 border-white/20 relative overflow-hidden group"
                        aria-label="Send message"
                      >
                        {/* Shimmer effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                        <Send className="w-5 h-5 relative z-10" />
                      </button>
                    </div>
                    <div className="flex items-center justify-center gap-2 mt-3">
                      <div className="h-1 w-1 rounded-full bg-emerald-400 animate-pulse" />
                      <p className="text-[10px] text-gray-400 font-bold tracking-wider">
                        REX • 28 AI AGENTS • CLAUDE SONNET 4.5
                      </p>
                    </div>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-10px) rotate(5deg); }
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-shimmer {
          animation: shimmer 3s infinite;
        }
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
