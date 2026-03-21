# tomo.ai Clone

A full-stack recreation of [tomo.ai](https://www.tomo.ai) — a personal AI assistant that helps you set goals and stay accountable.

## What is tomo.ai?

tomo.ai is an SMS-first personal AI that:
- Lives in your texts (no new app needed)
- Remembers your goals and checks in on progress
- Has a customizable personality (tough love vs gentle nudges)
- Connects to calendar, email, Notion, Google Drive

## This Clone

Built with:
- **Next.js 16** (App Router)
- **TypeScript**
- **Tailwind CSS 4**
- **Claude API** (`claude-haiku-4-5`) for AI responses
- **Lucide React** icons

### Pages
- `/` — Landing page (hero, features, how it works, pricing, testimonials)
- `/chat` — Full chat interface with AI responses

## Setup

```bash
cd tomo-clone
cp .env.local.example .env.local
# Edit .env.local and add your ANTHROPIC_API_KEY
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Architecture Analysis: How tomo.ai Works

### Frontend
- Modern dark-themed landing page (likely Next.js/React)
- SMS interface simulation on web
- Framer Motion animations

### Backend
- **SMS layer**: Twilio or similar (for real SMS delivery)
- **AI layer**: LLM (GPT-4o/Claude) with custom system prompt
- **Memory layer**: PostgreSQL or Redis for conversation history + user goals
- **Integrations**: OAuth for Google Calendar, Gmail, Notion

### Key Technical Patterns

1. **Persistent memory** — User goals and past conversations stored in DB, injected into system prompt as context
2. **Proactive messaging** — Cron jobs that trigger check-in messages via Twilio
3. **Personality system** — System prompt variations based on user preferences
4. **Integration webhooks** — OAuth + webhooks for calendar/email sync

### To Scale This

For a production version add:
- Twilio SMS: `twilio` npm package + webhook handler at `/api/sms`
- Auth: Clerk or NextAuth
- Database: Supabase/PostgreSQL with Prisma
- Cron reminders: Vercel Cron Jobs or Inngest
- Memory: Store conversation summaries per user session
