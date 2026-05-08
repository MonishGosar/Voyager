"use client";

/**
 * ConstraintForm — Trip planning constraints input form.
 *
 * This is Step 2 of the Voyager wizard. Users input their hard constraints:
 * destination, dates, budget, group configuration, and accessibility needs.
 * The component retrieves the VibeProfile from sessionStorage (set by VibeBoard)
 * and combines it with constraints to request an itinerary from the backend.
 *
 * On successful itinerary generation, the result is stored in sessionStorage
 * and the user is navigated to the Itinerary View (Step 3).
 *
 * @example
 * ```tsx
 * <Suspense fallback={<div>Loading...</div>}>
 *   <ConstraintForm />
 * </Suspense>
 * ```
 */

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Sparkles, Calendar as CalendarIcon, MapPin, Users,
  Coins, ArrowLeft, Accessibility, AlertTriangle
} from "lucide-react";
import type { VibeProfile, PlanningConstraints } from "@/types";
import { ItinerarySchema } from "@/lib/schemas";
import { apiUrl } from "@/lib/api";

/** Valid group type options. */
const GROUP_TYPES = ["Solo", "Couple", "Friends", "Family"] as const;

/** Supported currencies with display labels. */
const CURRENCIES = [
  { label: "USD $", value: "USD" },
  { label: "EUR €", value: "EUR" },
  { label: "INR ₹", value: "INR" },
  { label: "GBP £", value: "GBP" },
] as const;

/** Minimum viable daily budget per person in USD equivalent. */
const MIN_DAILY_BUDGET_USD: Record<string, number> = {
  USD: 20,
  EUR: 18,
  GBP: 16,
  INR: 1500,
};

/** Backend API URL for itinerary generation. */
const PLAN_API_URL = apiUrl("/api/plan");

export default function ConstraintForm(): JSX.Element {
  const router = useRouter();
  const searchParams = useSearchParams();

  // ── State ──────────────────────────────────────────────────────
  const [destination, setDestination] = useState<string>(
    searchParams.get("destination") || "Lisbon"
  );
  const [originCity, setOriginCity] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate]     = useState<string>("");
  const [groupType, setGroupType] = useState<string>("Couple");
  const [groupSize, setGroupSize] = useState<number>(2);
  const [currency, setCurrency]   = useState<string>("EUR");
  const [budget, setBudget]       = useState<string>("2000");
  const [wheelchair, setWheelchair]   = useState<boolean>(false);
  const [vegetarian, setVegetarian]   = useState<boolean>(false);
  const [loading, setLoading]         = useState<boolean>(false);
  const [error, setError]             = useState<string | null>(null);

  /**
   * Calculate the number of trip days from start and end dates.
   *
   * @returns The number of days (inclusive), or null if dates are invalid.
   */
  const numDays: number | null = (() => {
    if (!startDate || !endDate) return null;
    const diff = (new Date(endDate).getTime() - new Date(startDate).getTime()) / 86400000;
    return diff > 0 ? diff + 1 : null;
  })();

  const budgetNum = parseFloat(budget) || 0;
  const dailyPerPerson = numDays && groupSize > 0 ? budgetNum / numDays / groupSize : null;
  const minDaily = MIN_DAILY_BUDGET_USD[currency] ?? 20;
  const budgetTooLow = dailyPerPerson !== null && dailyPerPerson < minDaily;

  // Auto-set group size based on type
  useEffect(() => {
    if (groupType === "Solo") setGroupSize(1);
    else if (groupType === "Couple") setGroupSize(2);
  }, [groupType]);

  /**
   * Retrieve the vibe profile from sessionStorage.
   *
   * @returns The parsed VibeProfile object, or null if not available.
   */
  const getVibe = (): VibeProfile | null => {
    try {
      const raw = sessionStorage.getItem("voyager_vibe");
      return raw ? (JSON.parse(raw) as VibeProfile) : null;
    } catch {
      return null;
    }
  };

  /**
   * Submit constraints to the backend and generate an itinerary.
   *
   * Validates dates, builds the request payload, calls the /api/plan
   * endpoint, validates the response with Zod, stores it in sessionStorage,
   * and navigates to the itinerary page.
   */
  const buildItinerary = async (): Promise<void> => {
    if (!startDate || !endDate) {
      setError("Please select start and end dates.");
      return;
    }
    if (new Date(endDate) <= new Date(startDate)) {
      setError("End date must be after start date.");
      return;
    }
    setError(null);
    setLoading(true);

    const vibe = getVibe();

    const payload: Omit<PlanningConstraints, 'vibe'> & { vibe: VibeProfile | null } = {
      destination,
      startDate,
      endDate,
      groupType: groupType.toLowerCase(),
      groupSize,
      currency,
      budget: parseFloat(budget) || 0,
      pace: 2,
      accessibility: { wheelchair, vegetarian },
      must_include: [],
      exclude: [],
      origin_city: originCity.trim(),
      vibe,
    };

    try {
      const res = await fetch(PLAN_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const raw: unknown = await res.json();

      // Validate API response shape at runtime
      const parsed = ItinerarySchema.safeParse(raw);
      if (!parsed.success) {
        console.error("API contract mismatch:", parsed.error);
        throw new Error("Received malformed itinerary data from server.");
      }

      const itinerary = parsed.data;

      // Store itinerary + trip meta in session for the itinerary page
      sessionStorage.setItem("voyager_itinerary", JSON.stringify(itinerary));
      sessionStorage.setItem("voyager_trip_meta", JSON.stringify({
        destination,
        startDate,
        endDate,
        numDays,
        groupType,
        groupSize,
        currency,
        budget,
      }));

      router.push("/itinerary");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to generate itinerary. Please try again.";
      console.error("buildItinerary error:", err);
      setError(message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="bg-card text-card-foreground shadow-2xl w-96 p-10 space-y-8 rounded-3xl border border-blue-100">
          <div className="space-y-2 text-center">
            <p className="font-display text-2xl font-semibold text-blue-950">Building your itinerary</p>
            <p className="text-sm text-muted-foreground">Gemini is crafting your perfect trip…</p>
          </div>
          <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-blue-400 to-blue-600 animate-[progress_2s_ease-in-out_infinite]" />
          </div>
          <div className="space-y-3 text-sm text-muted-foreground text-center">
            <p>Reading your travel vibe…</p>
            <p className="text-blue-600 font-medium">Resolving budget constraints…</p>
            <p className="text-muted-foreground">Clustering stops by neighbourhood…</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-12 px-4 animate-fade-up">
      <div className="space-y-2 mb-10 text-center md:text-left">
        <h2 className="text-4xl md:text-5xl font-display font-semibold tracking-tight text-foreground">Plan your trip</h2>
        <p className="text-muted-foreground text-lg md:text-xl">Tell us the details — we'll handle the conflicts.</p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-3 text-sm text-red-700 font-medium">
          {error}
        </div>
      )}

      {/* ── Where & When ─────────────────────────────── */}
      <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-lg text-foreground">Where &amp; when</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Destination</label>
              <input
                className="flex h-12 w-full rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                value={destination}
                onChange={e => setDestination(e.target.value)}
                placeholder="e.g. Lisbon, Portugal"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Travelling from <span className="text-muted-foreground font-normal">(for travel cost estimate)</span>
              </label>
              <input
                className="flex h-12 w-full rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                value={originCity}
                onChange={e => setOriginCity(e.target.value)}
                placeholder="e.g. Mumbai, India"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label htmlFor="startDate" className="text-sm font-medium text-foreground">Start Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground pointer-events-none" />
                <input
                  id="startDate"
                  type="date"
                  className="flex h-12 w-full rounded-xl border border-input bg-transparent pl-12 pr-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 cursor-pointer"
                  value={startDate}
                  onChange={e => {
                    setStartDate(e.target.value);
                    // Auto push end date if it's before start
                    if (endDate && e.target.value >= endDate) setEndDate("");
                  }}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label htmlFor="endDate" className="text-sm font-medium text-foreground">End Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground pointer-events-none" />
                <input
                  id="endDate"
                  type="date"
                  className="flex h-12 w-full rounded-xl border border-input bg-transparent pl-12 pr-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 cursor-pointer"
                  value={endDate}
                  min={startDate || undefined}
                  onChange={e => setEndDate(e.target.value)}
                />
              </div>
            </div>
          </div>
          {numDays && (
            <p className="text-sm text-blue-600 font-medium">
              📅 {numDays} day{numDays > 1 ? "s" : ""} selected
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ── Group ───────────────────────────────────── */}
        <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-lg text-foreground">Group</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex flex-wrap gap-3">
              {GROUP_TYPES.map(type => (
                <button
                  key={type}
                  onClick={() => setGroupType(type)}
                  className={`px-5 py-2.5 rounded-full border text-sm font-medium transition-all duration-200 ${
                    groupType === type
                      ? "bg-blue-600 text-white border-blue-600 shadow-sm ring-2 ring-blue-600/20"
                      : "hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
            {groupType !== "Solo" && groupType !== "Couple" && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Number of people</label>
                <input
                  type="number"
                  min={2} max={20}
                  className="flex h-12 w-32 rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  value={groupSize}
                  onChange={e => setGroupSize(parseInt(e.target.value) || 2)}
                />
              </div>
            )}
          </div>
        </div>

        {/* ── Budget ─────────────────────────────────── */}
        <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
            <Coins className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-lg text-foreground">Budget &amp; style</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Total budget</label>
              <div className="flex gap-3">
                <select
                  className="h-12 rounded-xl border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 w-28"
                  value={currency}
                  onChange={e => setCurrency(e.target.value)}
                >
                  {CURRENCIES.map(c => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
                <input
                  type="number"
                  className="flex-1 h-12 rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
                  value={budget}
                  onChange={e => setBudget(e.target.value)}
                  placeholder="e.g. 2000"
                />
              </div>
            </div>
            {budgetTooLow && (
              <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5 text-amber-600" />
                <span>
                  {currency} {dailyPerPerson?.toFixed(0)}/person/day is very low for travel. Expect mostly free activities and budget accommodation. Consider increasing your budget for a fuller experience.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Accessibility ──────────────────────────────── */}
      <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <Accessibility className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-lg text-foreground">Preferences</h3>
        </div>
        <div className="p-6 flex flex-wrap gap-4">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={wheelchair}
              onChange={e => setWheelchair(e.target.checked)}
              className="h-5 w-5 rounded border-input accent-blue-600 cursor-pointer"
            />
            <span className="text-sm font-medium group-hover:text-blue-600 transition-colors">
              ♿ Wheelchair accessible stops only
            </span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={vegetarian}
              onChange={e => setVegetarian(e.target.checked)}
              className="h-5 w-5 rounded border-input accent-blue-600 cursor-pointer"
            />
            <span className="text-sm font-medium group-hover:text-blue-600 transition-colors">
              🌿 Vegetarian / vegan-friendly meals only
            </span>
          </label>
        </div>
      </div>

      {/* ── Actions ─────────────────────────────────────── */}
      <div className="pt-8 border-t flex flex-col sm:flex-row justify-between items-center gap-4">
        <button
          className="w-full sm:w-auto px-6 py-4 rounded-xl font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors flex items-center justify-center gap-2"
          onClick={() => router.push("/")}
        >
          <ArrowLeft className="h-5 w-5" />
          Back to Vibe Board
        </button>
        <button
          className="w-full sm:w-auto px-10 bg-blue-600 text-white hover:bg-blue-700 py-4 rounded-xl font-medium shadow-md flex items-center justify-center gap-2 transition-all hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          onClick={buildItinerary}
          disabled={!destination || !startDate || !endDate}
        >
          Build my itinerary
          <Sparkles className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
