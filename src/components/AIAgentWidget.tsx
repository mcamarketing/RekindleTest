import { useState, useRef, useEffect } from "react";
import {
  MessageCircle,
  X,
  Send,
  Sparkles,
  Minimize2,
  Loader2,
} from "lucide-react";
import { apiClient } from "../lib/api";
import { useAuth } from "../contexts/AuthContext";
import { supabase } from "../lib/supabase";
import { ChatMessage } from "./ChatMessage";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

interface RexResponse {
  conversation_id: string;
  response: string;
}

export function AIAgentWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [userFirstName, setUserFirstName] = useState<string | null>(null);

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    const greeting =
      hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
    const name = userFirstName || (user ? "there" : "");

    if (user) {
      return name
        ? `${greeting}, ${name}! \n\nI'm Rex, your Rekindle AI Expert. How can I help you today?`
        : `${greeting}! \n\nI'm Rex, your Rekindle AI Expert. How can I help you today?`;
    }
    return `${greeting}! 👋\n\nI'm Rex, your Rekindle AI Expert. Ask me about pricing, features, or how to get started!`;
  };

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: getWelcomeMessage(),
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchUserName = async () => {
      if (user?.id) {
        try {
          const { data, error } = await supabase
            .from("profiles")
            .select("first_name")
            .eq("id", user.id)
            .single();

          if (data && !error) {
            setUserFirstName(data.first_name);
          } else {
            const emailName = user.email?.split("@")[0] || null;
            setUserFirstName(emailName);
          }
        } catch (error) {
          console.error("Error fetching user name:", error);
          const emailName = user.email?.split("@")[0] || null;
          setUserFirstName(emailName);
        }
      }
    };

    fetchUserName();
  }, [user]);

  useEffect(() => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: getWelcomeMessage(),
        timestamp: new Date(),
      },
    ]);
  }, [user, userFirstName]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (messageText?: string) => {
    const messageToSend = messageText || input.trim();
    if (!messageToSend || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!messageText) setInput("");
    setIsLoading(true);

    try {
      const response = await apiClient.chatWithRex({
        message: messageToSend,
        conversation_id: conversationId,
      });

      if (response.success && response.data) {
        const responseData = response.data as RexResponse;
        if (responseData.conversation_id) {
          setConversationId(responseData.conversation_id);
        }
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: responseData.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I'm having trouble connecting. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, something went wrong. Please try again later.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-8 right-8 z-[9999] group"
        aria-label="Open AI Assistant"
      >
        <div className="relative w-16 h-16 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] shadow-2xl flex items-center justify-center transform transition-all duration-300 group-hover:scale-110">
          <MessageCircle className="w-7 h-7 text-white relative z-10" />
        </div>
      </button>
    );
  }

  return (
    <div
      className="fixed right-8 bottom-8 z-[9999] transition-all duration-300"
      style={{
        width: isMinimized ? "340px" : "420px",
        height: isMinimized ? "72px" : "min(680px, calc(100vh - 4rem))",
        maxHeight: "calc(100vh - 4rem)",
      }}
    >
      <div className="relative h-full rounded-3xl overflow-hidden shadow-2xl bg-slate-800 border border-slate-700">
        <div className="relative flex items-center justify-between p-4 bg-slate-900">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] flex items-center justify-center shadow-lg">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
            </div>

            <div>
              <h3 className="text-white font-bold text-base">Rex</h3>
              <p className="text-white/90 text-xs font-medium">
                Your AI Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
              aria-label={isMinimized ? "Expand" : "Minimize"}
            >
              <Minimize2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setIsOpen(false);
                setIsMinimized(false);
              }}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-all"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  userFirstName={userFirstName || undefined}
                  userEmail={user?.email || undefined}
                />
              ))}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] flex items-center justify-center flex-shrink-0 shadow-lg">
                    <Loader2 className="w-5 h-5 text-white animate-spin" />
                  </div>
                  <div className="bg-slate-700 rounded-2xl px-4 py-3 shadow-xl">
                    <div className="flex gap-1.5">
                      <div
                        className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce"
                        style={{ animationDelay: "0ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-[#F7931E] rounded-full animate-bounce"
                        style={{ animationDelay: "150ms" }}
                      />
                      <div
                        className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce"
                        style={{ animationDelay: "300ms" }}
                      />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="p-4 border-t border-slate-700">
              <div className="flex gap-2.5">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything..."
                  className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#FF6B35]/50 transition-all shadow-lg"
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className="w-12 h-12 bg-gradient-to-br from-[#FF6B35] to-[#F7931E] rounded-xl flex items-center justify-center text-white hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-xl"
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
