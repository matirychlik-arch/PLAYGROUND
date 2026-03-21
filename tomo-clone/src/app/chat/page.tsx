"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Send, Sparkles, Target, Bell, Calendar } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTED_GOALS = [
  "Wake up at 6am every day",
  "Work out 4x per week",
  "Read 30 minutes daily",
  "Quit social media after 9pm",
];

const QUICK_ACTIONS = [
  { icon: <Target className="w-4 h-4" />, label: "Set a goal" },
  { icon: <Bell className="w-4 h-4" />, label: "Add reminder" },
  { icon: <Calendar className="w-4 h-4" />, label: "Check my week" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hey! I'm Tomo 👋 I'm your personal AI — I'll help you set goals, stay accountable, and actually follow through. What's one thing you've been wanting to change or achieve lately?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;

    setShowSuggestions(false);
    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      });

      if (!res.ok) throw new Error("Failed to get response");

      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.content }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Hmm, I hit a snag 😅 Can you try again? (Make sure ANTHROPIC_API_KEY is set in .env.local)",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex flex-col">
      {/* Header */}
      <div className="glass border-b border-white/5 px-4 py-4 flex items-center gap-4 sticky top-0 z-10">
        <Link href="/" className="text-white/50 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center font-bold">
              T
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-[#0a0a0f]" />
          </div>
          <div>
            <p className="font-semibold">Tomo</p>
            <p className="text-xs text-green-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI · Always here
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin max-w-2xl w-full mx-auto">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} gap-3`}
          >
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-xs font-bold shrink-0 mt-1">
                T
              </div>
            )}
            <div
              className={`max-w-[80%] md:max-w-[65%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === "assistant"
                  ? "chat-bubble-ai rounded-tl-sm"
                  : "chat-bubble-user rounded-tr-sm"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex justify-start gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-xs font-bold shrink-0">
              T
            </div>
            <div className="chat-bubble-ai px-4 py-3 rounded-2xl rounded-tl-sm">
              <div className="flex gap-1 items-center h-4">
                <div className="typing-dot w-2 h-2 rounded-full bg-violet-400" />
                <div className="typing-dot w-2 h-2 rounded-full bg-violet-400" />
                <div className="typing-dot w-2 h-2 rounded-full bg-violet-400" />
              </div>
            </div>
          </div>
        )}

        {/* Goal suggestions */}
        {showSuggestions && messages.length === 1 && (
          <div className="mt-4">
            <p className="text-xs text-white/40 mb-3 ml-11">Quick start with a goal:</p>
            <div className="ml-11 flex flex-wrap gap-2">
              {SUGGESTED_GOALS.map((goal) => (
                <button
                  key={goal}
                  onClick={() => sendMessage(goal)}
                  className="text-xs px-3 py-2 glass rounded-full hover:bg-white/10 transition-colors text-white/70 hover:text-white border border-white/10"
                >
                  {goal}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Quick actions */}
      {messages.length > 1 && (
        <div className="px-4 pb-2 max-w-2xl w-full mx-auto">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                onClick={() => sendMessage(action.label)}
                className="flex items-center gap-1.5 shrink-0 text-xs px-3 py-2 glass rounded-full hover:bg-white/10 transition-colors text-white/60 hover:text-white border border-white/10"
              >
                {action.icon}
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="glass border-t border-white/5 px-4 py-4 sticky bottom-0">
        <form
          onSubmit={handleSubmit}
          className="max-w-2xl mx-auto flex gap-3 items-end"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message Tomo..."
            className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white placeholder-white/30 outline-none focus:border-violet-500/50 transition-colors resize-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="w-11 h-11 rounded-2xl bg-violet-600 hover:bg-violet-500 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-all shrink-0"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-center text-xs text-white/20 mt-2">
          Tomo may make mistakes. Don&apos;t rely on it for critical decisions.
        </p>
      </div>
    </div>
  );
}
