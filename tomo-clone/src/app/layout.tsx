import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tomo — Your AI for everything",
  description:
    "The personal AI that lives in your texts. Set goals, stay accountable, and actually follow through.",
  keywords: ["AI assistant", "goal tracking", "accountability", "personal AI"],
  openGraph: {
    title: "Tomo — Your AI for everything",
    description: "The personal AI that helps you actually follow through on your goals.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="antialiased">{children}</body>
    </html>
  );
}
