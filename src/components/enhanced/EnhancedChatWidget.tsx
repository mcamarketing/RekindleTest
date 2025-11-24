/**
 * Enhanced AI Chat Widget
 * Floating chat interface with smooth animations
 * Maintains RekindlePro branding
 */

import { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Minimize2, Maximize2, Loader, Brain, Sparkles } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface EnhancedChatWidgetProps {
  onSendMessage: (message: string) => Promise<string>;
  initialOpen?: boolean;
}

export const EnhancedChatWidget = ({
  onSendMessage,
  initialOpen = false
}: EnhancedChatWidgetProps) => {
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your RekindlePro AI assistant. I can help you with lead reactivation, campaign setup, and performance insights. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSend = async () => {
    if (!inputValue.trim() || isSending) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsSending(true);
    setIsTyping(true);

    try {
      const response = await onSendMessage(userMessage.content);

      setIsTyping(false);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      setIsTyping(false);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { label: "Reactivate Leads", icon: Sparkles },
    { label: "Campaign Performance", icon: Brain },
    { label: "Setup Guide", icon: MessageSquare },
  ];

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] rounded-full shadow-2xl shadow-[#FF6B35]/50 flex items-center justify-center hover:scale-110 transition-transform duration-300 group"
        >
          <div className="relative">
            <MessageSquare className="w-7 h-7 text-white" />
            {/* Pulse Animation */}
            <span className="absolute inset-0 rounded-full bg-[#FF6B35] animate-ping opacity-20"></span>
          </div>

          {/* Unread Badge (optional) */}
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
            1
          </div>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div
          className={`fixed bottom-6 right-6 z-50 w-96 bg-gradient-to-br from-[#1A1F2E] to-[#242938] rounded-2xl shadow-2xl border border-[#FF6B35]/30 flex flex-col transition-all duration-300 ${
            isMinimized ? 'h-16' : 'h-[600px]'
          }`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gradient-to-r from-[#FF6B35]/10 to-[#F7931E]/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#FF6B35] to-[#F7931E] flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-bold text-sm">RekindlePro AI</h3>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span className="text-xs text-gray-400">Online</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4 text-gray-400 hover:text-white" />
                ) : (
                  <Minimize2 className="w-4 h-4 text-gray-400 hover:text-white" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-gray-400 hover:text-white" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white'
                          : 'bg-[#0a0e1a] text-gray-300 border border-gray-700'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <span className="text-xs opacity-60 mt-1 block">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="bg-[#0a0e1a] border border-gray-700 rounded-2xl px-4 py-3 flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-[#F7931E] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-xs text-gray-400">AI is typing...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Quick Actions */}
              {messages.length === 1 && (
                <div className="px-4 pb-3">
                  <div className="text-xs text-gray-500 mb-2">Quick actions:</div>
                  <div className="flex flex-wrap gap-2">
                    {quickActions.map((action) => {
                      const Icon = action.icon;
                      return (
                        <button
                          key={action.label}
                          onClick={() => {
                            setInputValue(action.label);
                            inputRef.current?.focus();
                          }}
                          className="px-3 py-1.5 bg-[#0a0e1a] border border-gray-700 hover:border-[#FF6B35] rounded-full text-xs text-gray-400 hover:text-white transition-all flex items-center gap-1.5"
                        >
                          <Icon className="w-3 h-3" />
                          {action.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Input Area */}
              <div className="p-4 border-t border-gray-700">
                <div className="flex items-center gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    disabled={isSending}
                    className="flex-1 px-4 py-3 bg-[#0a0e1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:border-[#FF6B35] focus:ring-2 focus:ring-[#FF6B35]/20 transition-all text-sm disabled:opacity-50"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!inputValue.trim() || isSending}
                    className="px-4 py-3 bg-gradient-to-r from-[#FF6B35] to-[#F7931E] text-white rounded-xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center"
                  >
                    {isSending ? (
                      <Loader className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

/**
 * Example Usage:
 *
 * function App() {
 *   const handleSendMessage = async (message: string) => {
 *     const response = await fetch('/api/chat', {
 *       method: 'POST',
 *       headers: { 'Content-Type': 'application/json' },
 *       body: JSON.stringify({ message })
 *     });
 *     const data = await response.json();
 *     return data.response;
 *   };
 *
 *   return (
 *     <div>
 *       {/* Your app content *}
 *       <EnhancedChatWidget onSendMessage={handleSendMessage} />
 *     </div>
 *   );
 * }
 */
