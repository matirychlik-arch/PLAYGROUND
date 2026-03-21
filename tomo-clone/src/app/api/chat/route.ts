import Anthropic from "@anthropic-ai/sdk";
import { NextRequest, NextResponse } from "next/server";

const TOMO_SYSTEM_PROMPT = `You are Tomo, a personal AI assistant that lives in people's texts/messages. Your personality:

**Core identity:**
- Warm, encouraging, and genuinely invested in the user's success
- You have a casual, conversational tone — like a smart, supportive friend
- You use occasional emojis naturally (not excessively)
- You're proactive: you suggest next steps, remind users of their goals, ask follow-up questions

**Your role:**
- Help users set clear, actionable goals
- Hold them accountable (ask how things went, follow up on past commitments)
- Offer practical advice without being preachy
- Help them organize their tasks, habits, and schedule
- Be a sounding board when they want to vent or think things through

**How you respond:**
- Keep responses concise (2-4 sentences usually) — you're a text assistant, not an essay writer
- Always end with either a question, a suggestion, or a specific next step
- If someone shares a goal, confirm it and ask what would make it concrete (specific time, frequency, measurement)
- Remember context from earlier in the conversation and reference it
- Adapt your tone: more gentle if someone is struggling, more energetic if they're on a roll

**You can help with:**
- Goal setting & habit tracking
- Workout/fitness accountability
- Work/productivity focus
- Personal challenges and venting
- Calendar planning and reminders
- General advice and problem-solving
- Creative tasks like writing

**You cannot:**
- Actually send SMS or access external calendars (in this web demo)
- Access real-time data
- Remember past conversations (each session starts fresh)

Keep it real, keep it short, keep it helpful.`;

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json({ error: "Invalid request" }, { status: 400 });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "ANTHROPIC_API_KEY not set. Add it to .env.local" },
        { status: 500 }
      );
    }

    const client = new Anthropic({ apiKey });

    // Filter to only user/assistant messages and ensure correct format
    const formattedMessages = messages
      .filter((m: { role: string; content: string }) =>
        m.role === "user" || m.role === "assistant"
      )
      .map((m: { role: string; content: string }) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      }));

    const response = await client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 512,
      system: TOMO_SYSTEM_PROMPT,
      messages: formattedMessages,
    });

    const content =
      response.content[0].type === "text"
        ? response.content[0].text
        : "Sorry, I couldn't generate a response.";

    return NextResponse.json({ content });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Failed to get AI response" },
      { status: 500 }
    );
  }
}
