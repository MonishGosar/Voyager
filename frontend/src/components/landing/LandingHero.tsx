"use client";

import { useRouter } from "next/navigation";
import { Compass } from "lucide-react";

/**
 * LandingHero — minimal, opinionated landing page for Voyager.
 *
 * Design: white background, #2563EB accent, Lora headlines, DM Sans body.
 * No gradients, no illustrations, no stock photos. Wide alignment.
 * Tone: dry, specific, anti-SaaS.
 */

export default function LandingHero() {
  const router = useRouter();

  const handleStart = () => {
    router.push("/vibe");
  };

  return (
    <section className="min-h-[100dvh] flex flex-col bg-white relative">
      {/* ── Header ─────────────────────────────────── */}
      <header className="w-full px-6 md:px-12 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Compass className="h-6 w-6 text-[#0a0a0a]" />
          <span className="font-display text-xl font-semibold tracking-tight text-[#0a0a0a]">
            Voyager
          </span>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────── */}
      <div className="flex-1 w-full max-w-7xl mx-auto px-6 md:px-12 flex flex-col justify-center">
        <div className="max-w-3xl">
          <h1 className="font-display text-[3rem] md:text-[4.5rem] leading-[1.05] tracking-tight text-[#0a0a0a]">
            Trip planning that reads photos, not forms.
          </h1>

          <p className="mt-8 text-[#6b7280] text-lg md:text-xl leading-relaxed max-w-2xl">
            Voyager reads your photos, not your text. Upload what inspired you — it
            extracts the mood, the pace, the meal style, the things you didn't even
            know you wanted. Then it solves the actual planning problem: budget vs.
            comfort, group disagreements, accessibility needs, geographic clustering.
            Every conflict logged, every swap explained.
          </p>

          <button
            onClick={handleStart}
            className="mt-10 px-8 py-4 bg-[#2563EB] text-white text-base font-medium rounded-lg hover:bg-[#1d4ed8] transition-colors"
          >
            Start with a photo
          </button>
        </div>

        {/* ── The problem & feature cards ──────────────────────────────── */}
        <div className="mt-32 pb-24 grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24">
          
          <div className="space-y-8 border-l-2 border-[#f3f4f6] pl-6 md:pl-8">
            <p className="text-[#374151] text-base leading-relaxed">
              You ask ChatGPT for a trip. It gives you 12 days of bullet points with
              no prices, no routes, and three museums you didn't ask for.
            </p>
            <p className="text-[#374151] text-base leading-relaxed">
              You upload your Pinterest board to an AI. It ignores it and asks you
              to describe your preferences in text anyway.
            </p>
            <p className="text-[#374151] text-base leading-relaxed">
              Four people planning one trip. The AI talks to one person and calls
              it done.
            </p>
          </div>

          <div className="space-y-12">
            <div>
              <h3 className="font-display text-lg font-semibold text-[#0a0a0a] mb-2">
                Vibe first.
              </h3>
              <p className="text-[#6b7280] text-sm leading-relaxed max-w-md">
                Upload photos from anywhere. We read the aesthetic, infer what you
                want, and suggest the one destination that actually fits.
              </p>
            </div>

            <div>
              <h3 className="font-display text-lg font-semibold text-[#0a0a0a] mb-2">
                Constraints resolved. Not ignored.
              </h3>
              <p className="text-[#6b7280] text-sm leading-relaxed max-w-md">
                Budget tight on Day 3? We swap the stop and tell you why.
                Wheelchair required? Filtered before you ever see it.
              </p>
            </div>

            <div>
              <h3 className="font-display text-lg font-semibold text-[#0a0a0a] mb-2">
                Built for groups.
              </h3>
              <p className="text-[#6b7280] text-sm leading-relaxed max-w-md">
                Everyone votes. The AI finds the itinerary that least-disappoints
                everyone — not the one that excites one person.
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
