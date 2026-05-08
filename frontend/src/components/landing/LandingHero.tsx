"use client";

/**
 * LandingHero — The main landing page hero section.
 *
 * Presents the Voyager value proposition with a "status quo vs. Voyager way"
 * comparison layout. Contains the primary CTA button that navigates users
 * to the Vibe Board (Step 1).
 *
 * This component is a server-rendered page component that uses client-side
 * navigation via Next.js router.
 *
 * @example
 * ```tsx
 * <LandingHero />
 * ```
 */

import { useRouter } from "next/navigation";
import { Compass, Bot, ImagePlus, Users, Camera, Settings2, UsersRound } from "lucide-react";

export default function LandingHero(): JSX.Element {
  const router = useRouter();

  return (
    <section className="min-h-[100dvh] flex flex-col bg-white relative selection:bg-blue-100 overflow-hidden">
      {/* subtle grid background */}
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:48px_48px] opacity-40" />
      <div className="pointer-events-none absolute top-0 left-0 right-0 h-[500px] bg-gradient-to-b from-blue-50/60 to-transparent" />

      {/* ── Header ─────────────────────────────────── */}
      <header className="relative w-full max-w-6xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Compass className="h-6 w-6 text-[#0a0a0a]" />
          <span className="font-display text-xl font-semibold tracking-tight text-[#0a0a0a]">
            Voyager
          </span>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────── */}
      <div className="relative flex-1 w-full max-w-6xl mx-auto px-6 pt-16 pb-32 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-medium mb-8">
          <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
          AI-powered trip planning
        </div>

        <h1 className="font-display text-[3.2rem] md:text-[5rem] leading-[1.05] tracking-tight text-[#0a0a0a] max-w-4xl mx-auto">
          Trip planning that{" "}
          <span className="relative inline-block">
            <span className="relative z-10 text-blue-600">reads photos</span>
            <span className="absolute bottom-2 left-0 right-0 h-3 bg-blue-100/80 -z-10 rounded-sm" />
          </span>
          , not forms.
        </h1>

        <p className="mt-8 text-[#6b7280] text-lg md:text-xl leading-relaxed max-w-2xl mx-auto">
          Drop your inspiration photos. Voyager reads the aesthetic, resolves budget conflicts, and builds a real itinerary — every swap explained.
        </p>

        <button
          onClick={() => router.push("/vibe")}
          className="group mt-12 px-8 py-4 bg-[#2563EB] text-white text-base font-medium rounded-xl hover:bg-[#1d4ed8] hover:shadow-xl hover:-translate-y-1 transition-all duration-200 shadow-md shadow-blue-200 flex items-center gap-2"
        >
          Start with a photo
          <svg className="h-4 w-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
        </button>

        <p className="mt-4 text-xs text-muted-foreground">No account needed · Powered by Gemini</p>

        {/* ── The Problem vs The Solution ──────────────────────────────── */}
        <div className="mt-40 w-full grid grid-cols-1 md:grid-cols-2 gap-12 text-left">

          {/* Problem Column */}
          <div className="space-y-10">
            <div className="flex items-center gap-3 pb-4 border-b border-gray-100">
              <span className="h-2 w-2 rounded-full bg-gray-400" />
              <h2 className="font-display text-xl font-semibold text-[#6b7280]">The status quo</h2>
            </div>

            {[
              { Icon: Bot, text: "You ask ChatGPT for a trip. It gives you 12 days of bullet points with no prices, no routes, and three museums you didn't ask for." },
              { Icon: ImagePlus, text: "You upload your Pinterest board to an AI. It ignores it and asks you to describe your preferences in text anyway." },
              { Icon: Users, text: "Four people planning one trip. The AI talks to one person and calls it done." },
            ].map(({ Icon, text }, i) => (
              <div key={i} className="flex gap-4 items-start">
                <div className="mt-0.5 bg-gray-50 p-2 rounded-lg shrink-0">
                  <Icon className="w-4 h-4 text-gray-400" strokeWidth={1.5} />
                </div>
                <p className="text-[#374151] text-[15px] leading-relaxed">{text}</p>
              </div>
            ))}
          </div>

          {/* Solution Column */}
          <div className="space-y-10">
            <div className="flex items-center gap-3 pb-4 border-b border-blue-100">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              <h2 className="font-display text-xl font-semibold text-blue-700">The Voyager way</h2>
            </div>

            {[
              { Icon: Camera, title: "Vibe first.", text: "Upload photos from anywhere. We read the aesthetic, infer what you want, and suggest the destination that actually fits." },
              { Icon: Settings2, title: "Constraints resolved.", text: "Budget tight on Day 3? We swap the stop and tell you why. Wheelchair required? Filtered before you ever see it." },
              { Icon: UsersRound, title: "Built for groups.", text: "Everyone votes. The AI finds the itinerary that least-disappoints everyone — not the one that excites one person." },
            ].map(({ Icon, title, text }, i) => (
              <div key={i} className="flex gap-4 items-start">
                <div className="mt-0.5 bg-blue-50 p-2 rounded-lg shrink-0 border border-blue-100">
                  <Icon className="w-4 h-4 text-blue-600" strokeWidth={1.5} />
                </div>
                <div>
                  <h3 className="font-semibold text-[15px] text-[#0a0a0a] mb-1">{title}</h3>
                  <p className="text-[#6b7280] text-[14px] leading-relaxed">{text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
