import { motion } from "framer-motion";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
  userFirstName?: string;
  userEmail?: string;
}

export function ChatMessage({
  message,
  userFirstName,
  userEmail,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#FF6B35] to-[#F7931E] flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white/20">
          <span className="text-white font-bold text-sm">R</span>
        </div>
      )}
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-xl transition-all hover:scale-[1.01] ${
          isUser
            ? "bg-gradient-to-br from-[#FF6B35] to-[#F7931E] text-white"
            : "bg-white/10 backdrop-blur-sm text-gray-100 border border-white/20"
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
        <p className="text-xs opacity-70 mt-2 font-medium">
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
      {isUser && (
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center flex-shrink-0 shadow-lg border-2 border-white/10">
          <span className="text-sm text-white font-bold">
            {userFirstName?.charAt(0).toUpperCase() ||
              userEmail?.charAt(0).toUpperCase() ||
              "U"}
          </span>
        </div>
      )}
    </motion.div>
  );
}
