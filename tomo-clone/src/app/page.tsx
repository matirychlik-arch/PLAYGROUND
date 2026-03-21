"use client";

import { useState } from "react";
import Link from "next/link";
import { MessageCircle, Target, Bell, Calendar, Zap, Star, ArrowRight, CheckCircle, Brain, Heart, Sparkles } from "lucide-react";

const DEMO_MESSAGES = [
  { role: "ai", text: "Hey! I'm Tomo 👋 What's one goal you've been putting off?" },
  { role: "user", text: "I want to get up at 6am every day and work out" },
  { role: "ai", text: "Love it 💪 I'll remind you tomorrow at 5:55am. What's stopping you so far — motivation or just not sleeping early enough?" },
  { role: "user", text: "Honestly just staying up too late on my phone" },
  { role: "ai", text: "Classic trap. Let's fix that — want me to send you a 'wind down' reminder at 10pm? I'll also check in Friday to see how the week went 🎯" },
];

const FEATURES = [
  {
    icon: <MessageCircle className="w-5 h-5" />,
    title: "Lives in your texts",
    desc: "No new app to open. Tomo fits into where you already spend time — your messages.",
  },
  {
    icon: <Target className="w-5 h-5" />,
    title: "Goal accountability",
    desc: "Tomo remembers what you said you'd do — and actually follows up. No more empty promises to yourself.",
  },
  {
    icon: <Bell className="w-5 h-5" />,
    title: "Smart reminders",
    desc: "Proactive check-ins at the right moment, not random pings. Tomo learns your rhythm.",
  },
  {
    icon: <Calendar className="w-5 h-5" />,
    title: "Calendar & email sync",
    desc: "Connects to Google Calendar, Gmail, Notion, and more. Your AI that actually knows your schedule.",
  },
  {
    icon: <Brain className="w-5 h-5" />,
    title: "Memory that matters",
    desc: "Tomo remembers your context, goals, preferences, and progress across every conversation.",
  },
  {
    icon: <Heart className="w-5 h-5" />,
    title: "Personality you choose",
    desc: "Tough love or gentle nudges — you decide how Tomo keeps you accountable.",
  },
];

const TESTIMONIALS = [
  {
    text: "Nothing stuck until Tomo. It's like having a friend who actually remembers what you said you'd do.",
    author: "Sarah M.",
    role: "Product Designer",
  },
  {
    text: "I use it for calorie tracking, writing help, and venting. It does it all without me switching apps.",
    author: "Jake T.",
    role: "Software Engineer",
  },
  {
    text: "The check-ins are what make it different. It doesn't let me forget my goals.",
    author: "Priya K.",
    role: "Founder",
  },
];

export default function LandingPage() {
  const [demoStep, setDemoStep] = useState(0);
  const [showAll, setShowAll] = useState(false);

  const visibleMessages = showAll ? DEMO_MESSAGES : DEMO_MESSAGES.slice(0, demoStep + 1);

  const handleNextDemo = () => {
    if (demoStep < DEMO_MESSAGES.length - 1) {
      setDemoStep((s) => s + 1);
    } else {
      setShowAll(true);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 glass border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-sm font-bold">
              T
            </div>
            <span className="font-semibold text-lg">tomo</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-white/60">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how" className="hover:text-white transition-colors">How it works</a>
            <a href="#reviews" className="hover:text-white transition-colors">Reviews</a>
          </div>
          <Link
            href="/chat"
            className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-4 py-2 rounded-full transition-colors"
          >
            Try for free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 relative">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 right-1/4 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl" />
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-2 text-sm text-white/70 mb-8">
            <Sparkles className="w-4 h-4 text-violet-400" />
            <span>50,000+ people use Tomo daily</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
            The AI that{" "}
            <span className="gradient-text">lives in</span>
            <br />
            your texts
          </h1>

          <p className="text-xl text-white/60 max-w-2xl mx-auto mb-10 leading-relaxed">
            Tell Tomo your goals. Tomo holds you accountable, checks in daily,
            and organizes your life to make sure you actually follow through.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/chat"
              className="glow-pulse flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-8 py-4 rounded-2xl text-lg font-medium transition-all hover:scale-105"
            >
              Start chatting free
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#demo"
              className="flex items-center gap-2 glass hover:bg-white/5 text-white px-8 py-4 rounded-2xl text-lg font-medium transition-all"
            >
              See demo
            </a>
          </div>

          <p className="mt-4 text-sm text-white/40">No credit card. No app download. Works via SMS or web.</p>
        </div>
      </section>

      {/* Demo */}
      <section id="demo" className="py-16 px-6">
        <div className="max-w-md mx-auto">
          <div className="glass rounded-3xl p-4 overflow-hidden">
            {/* Phone header */}
            <div className="flex items-center gap-3 pb-4 border-b border-white/10 mb-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center font-bold">
                T
              </div>
              <div>
                <p className="font-semibold text-sm">Tomo</p>
                <p className="text-xs text-green-400">● Online</p>
              </div>
            </div>

            {/* Messages */}
            <div className="space-y-3 min-h-[280px]">
              {visibleMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                      msg.role === "ai" ? "chat-bubble-ai" : "chat-bubble-user"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Next button */}
            {!showAll && (
              <button
                onClick={handleNextDemo}
                className="mt-4 w-full py-3 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-300 text-sm hover:bg-violet-600/30 transition-colors"
              >
                {demoStep < DEMO_MESSAGES.length - 1 ? "Continue conversation →" : "See full chat →"}
              </button>
            )}
            {showAll && (
              <Link
                href="/chat"
                className="mt-4 flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-violet-600 text-white text-sm font-medium hover:bg-violet-500 transition-colors"
              >
                Start your conversation <ArrowRight className="w-4 h-4" />
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Everything you need,{" "}
              <span className="gradient-text">nothing you don&apos;t</span>
            </h2>
            <p className="text-white/60 text-lg max-w-xl mx-auto">
              Tomo is designed to be the one AI that actually fits in your life.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map((f, i) => (
              <div key={i} className="glass rounded-2xl p-6 hover:bg-white/5 transition-colors group">
                <div className="w-10 h-10 rounded-xl bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-violet-400 mb-4 group-hover:bg-violet-600/30 transition-colors">
                  {f.icon}
                </div>
                <h3 className="font-semibold mb-2">{f.title}</h3>
                <p className="text-white/50 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="py-24 px-6 bg-gradient-to-b from-transparent via-violet-950/10 to-transparent">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How it works</h2>
          </div>

          <div className="space-y-6">
            {[
              { step: "01", title: "Tell Tomo your goals", desc: "Share what you want to achieve — fitness, work, habits, anything. Tomo listens and remembers." },
              { step: "02", title: "Tomo learns your rhythm", desc: "Over the first few days, Tomo figures out when to check in and how you communicate best." },
              { step: "03", title: "Daily check-ins & accountability", desc: "Tomo proactively reaches out, follows up on what you said, and adjusts if life gets in the way." },
              { step: "04", title: "Connect your tools (optional)", desc: "Link Google Calendar, Gmail, or Notion so Tomo has full context and can act on your behalf." },
            ].map((item) => (
              <div key={item.step} className="glass rounded-2xl p-6 flex gap-6 items-start">
                <div className="text-4xl font-bold text-violet-500/30 shrink-0 w-12">{item.step}</div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                  <p className="text-white/50 text-sm leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="reviews" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              People actually{" "}
              <span className="gradient-text">follow through now</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {TESTIMONIALS.map((t, i) => (
              <div key={i} className="glass rounded-2xl p-6">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, s) => (
                    <Star key={s} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-white/70 text-sm leading-relaxed mb-4">&ldquo;{t.text}&rdquo;</p>
                <div>
                  <p className="font-medium text-sm">{t.author}</p>
                  <p className="text-white/40 text-xs">{t.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Simple pricing</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <div className="glass rounded-2xl p-6">
              <h3 className="font-semibold text-lg mb-1">Free</h3>
              <p className="text-3xl font-bold mb-1">$0</p>
              <p className="text-white/50 text-sm mb-6">50 messages / month</p>
              <ul className="space-y-3 mb-8">
                {["Goal tracking", "Daily check-ins", "Basic reminders"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                    <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link href="/chat" className="block text-center py-3 rounded-xl border border-white/20 hover:bg-white/5 transition-colors text-sm">
                Get started
              </Link>
            </div>

            <div className="rounded-2xl p-6 bg-gradient-to-br from-violet-600/20 to-blue-600/20 border border-violet-500/30 relative">
              <div className="absolute top-4 right-4 bg-violet-500 text-white text-xs px-2 py-1 rounded-full">Popular</div>
              <h3 className="font-semibold text-lg mb-1">Pro</h3>
              <p className="text-3xl font-bold mb-1">$15<span className="text-lg font-normal text-white/50">/mo</span></p>
              <p className="text-white/50 text-sm mb-6">Unlimited messages</p>
              <ul className="space-y-3 mb-8">
                {["Everything in Free", "Unlimited messages", "Calendar & email sync", "Notion integration", "Group chat support", "Custom personality"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-white/70">
                    <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <Link href="/chat" className="block text-center py-3 rounded-xl bg-violet-600 hover:bg-violet-500 transition-colors text-sm font-medium">
                Start free trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <div className="glass rounded-3xl p-12">
            <Zap className="w-12 h-12 text-violet-400 mx-auto mb-6" />
            <h2 className="text-4xl font-bold mb-4">
              Ready to actually{" "}
              <span className="gradient-text">follow through?</span>
            </h2>
            <p className="text-white/60 mb-8">
              Join 50,000+ people who use Tomo to stop procrastinating and start achieving.
            </p>
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white px-10 py-4 rounded-2xl text-lg font-medium transition-all hover:scale-105"
            >
              Start for free
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/40">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center text-xs font-bold text-white">T</div>
            <span>tomo © 2025</span>
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-white transition-colors">Privacy</a>
            <a href="#" className="hover:text-white transition-colors">Terms</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
