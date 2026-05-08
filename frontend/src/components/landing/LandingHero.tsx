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
    <section className="min-h-[100dvh] flex flex-col bg-white relative selection:bg-blue-100">
      {/* ── Header ─────────────────────────────────── */}
      <header className="w-full max-w-6xl mx-auto px-6 py-8 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Compass className="h-6 w-6 text-[#0a0a0a]" />
          <span className="font-display text-xl font-semibold tracking-tight text-[#0a0a0a]">
            Voyager
          </span>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────── */}
      <div className="flex-1 w-full max-w-6xl mx-auto px-6 pt-20 pb-32 flex flex-col items-center text-center">
        <h1 className="font-display text-[3.5rem] md:text-[5rem] leading-[1.05] tracking-tight text-[#0a0a0a] max-w-4xl mx-auto">
          Trip planning that reads photos, not forms.
        </h1>

        <p className="mt-8 text-[#6b7280] text-lg md:text-xl leading-relaxed max-w-2xl mx-auto">
          Voyager reads your photos, not your text. It extracts your vibe and solves the actual planning problem: budget limits, group votes, accessibility, and geography. Every conflict logged, every swap explained.
        </p>

        <button
          onClick={() => router.push("/vibe")}
          className="mt-12 px-8 py-4 bg-[#2563EB] text-white text-base font-medium rounded-lg hover:bg-[#1d4ed8] hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200"
        >
          Start with a photo
        </button>

        {/* ── The Problem vs The Solution ──────────────────────────────── */}
        <div className="mt-40 w-full grid grid-cols-1 md:grid-cols-2 gap-20 text-left">
          
          {/* Problem Column */}
          <div className="space-y-12">
            <h2 className="font-display text-2xl font-medium text-[#0a0a0a] border-b border-gray-100 pb-4">
              The status quo
            </h2>
            
            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-gray-50 p-2 rounded-md">
                <Bot className="w-5 h-5 text-gray-500" strokeWidth={1.5} />
              </div>
              <p className="text-[#374151] text-[15px] leading-relaxed">
                You ask ChatGPT for a trip. It gives you 12 days of bullet points with
                no prices, no routes, and three museums you didn't ask for.
              </p>
            </div>
            
            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-gray-50 p-2 rounded-md">
                <ImagePlus className="w-5 h-5 text-gray-500" strokeWidth={1.5} />
              </div>
              <p className="text-[#374151] text-[15px] leading-relaxed">
                You upload your Pinterest board to an AI. It ignores it and asks you
                to describe your preferences in text anyway.
              </p>
            </div>
            
            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-gray-50 p-2 rounded-md">
                <Users className="w-5 h-5 text-gray-500" strokeWidth={1.5} />
              </div>
              <p className="text-[#374151] text-[15px] leading-relaxed">
                Four people planning one trip. The AI talks to one person and calls
                it done.
              </p>
            </div>
          </div>

          {/* Solution Column */}
          <div className="space-y-12">
            <h2 className="font-display text-2xl font-medium text-[#0a0a0a] border-b border-gray-100 pb-4">
              The Voyager way
            </h2>
            
            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-blue-50 p-2 rounded-md">
                <Camera className="w-5 h-5 text-blue-600" strokeWidth={1.5} />
              </div>
              <div>
                <h3 className="font-display text-[15px] font-semibold text-[#0a0a0a] mb-1">Vibe first.</h3>
                <p className="text-[#6b7280] text-[14px] leading-relaxed">
                  Upload photos from anywhere. We read the aesthetic, infer what you
                  want, and suggest the destination that actually fits.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-blue-50 p-2 rounded-md">
                <Settings2 className="w-5 h-5 text-blue-600" strokeWidth={1.5} />
              </div>
              <div>
                <h3 className="font-display text-[15px] font-semibold text-[#0a0a0a] mb-1">Constraints resolved.</h3>
                <p className="text-[#6b7280] text-[14px] leading-relaxed">
                  Budget tight on Day 3? We swap the stop and tell you why.
                  Wheelchair required? Filtered before you ever see it.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="mt-1 bg-blue-50 p-2 rounded-md">
                <UsersRound className="w-5 h-5 text-blue-600" strokeWidth={1.5} />
              </div>
              <div>
                <h3 className="font-display text-[15px] font-semibold text-[#0a0a0a] mb-1">Built for groups.</h3>
                <p className="text-[#6b7280] text-[14px] leading-relaxed">
                  Everyone votes. The AI finds the itinerary that least-disappoints
                  everyone — not the one that excites one person.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
