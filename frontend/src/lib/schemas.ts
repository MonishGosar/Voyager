/**
 * Zod schemas for runtime validation of API responses.
 *
 * These schemas validate that API responses from the backend match
 * the expected shape at runtime, catching contract mismatches early.
 *
 * Each schema corresponds exactly to a TypeScript interface in types/index.ts
 * and a Pydantic model in the backend.
 *
 * @example
 * ```ts
 * import { VibeProfileSchema } from "@/lib/schemas";
 *
 * const res = await fetch("/api/vibe", { method: "POST", body: formData });
 * const data = await res.json();
 * const parsed = VibeProfileSchema.safeParse(data);
 * if (!parsed.success) {
 *   console.error("API contract violation:", parsed.error);
 * }
 * ```
 */

import { z } from "zod";

// ──────────────────────────────────────────────
// Vibe Schemas
// ──────────────────────────────────────────────

/** Schema for PlaceSignal — a signal from a mood board photo. */
export const PlaceSignalSchema = z.object({
  type: z.string(),
  vibe: z.string(),
});

/** Schema for Destination — a suggested travel destination. */
export const DestinationSchema = z.object({
  name: z.string(),
  country: z.string(),
});

/**
 * Schema for VibeProfile — the full vibe analysis response.
 *
 * Validates the response from POST /api/vibe.
 */
export const VibeProfileSchema = z.object({
  tags: z.array(z.string()),
  mood: z.string(),
  travel_style: z.string(),
  pace: z.string(),
  place_signals: z.array(PlaceSignalSchema),
  must_haves: z.array(z.string()),
  avoid_hints: z.array(z.string()),
  suggested_destinations: z.array(DestinationSchema),
  meal_style: z.string(),
  time_of_day_preference: z.string(),
});

// ──────────────────────────────────────────────
// Itinerary Schemas
// ──────────────────────────────────────────────

/** Schema for TravelToNext — transit between consecutive stops. */
export const TravelToNextSchema = z.object({
  duration: z.string(),
  mode: z.string(),
});

/**
 * Schema for Stop — a single itinerary stop.
 *
 * Validates each stop in the day plan, including accessibility
 * flags, cost data, and optional transit/fallback info.
 */
export const StopSchema = z.object({
  time: z.string(),
  name: z.string(),
  description: z.string(),
  neighborhood: z.string().default(""),
  wheelchair: z.boolean(),
  vegetarian: z.boolean(),
  stepFree: z.boolean(),
  cost: z.string(),
  priceLevel: z.number().int().min(0).max(4),
  streetViewUrl: z.string(),
  travelToNext: TravelToNextSchema.nullable().default(null),
  rainy_day_fallback: z.string().default(""),
});

/** Schema for DayPlan — a single day with stops and total cost. */
export const DayPlanSchema = z.object({
  stops: z.array(StopSchema),
  totalCost: z.string(),
});

/**
 * Schema for Itinerary — the full itinerary response.
 *
 * Validates the response from POST /api/plan.
 */
export const ItinerarySchema = z.object({
  days: z.array(DayPlanSchema),
  conflicts_resolved: z.array(z.string()),
  total_estimated_cost: z.number(),
  accessibility_notes: z.string(),
});

// ──────────────────────────────────────────────
// API Error Schema
// ──────────────────────────────────────────────

/** Schema for standard API error responses from the backend. */
export const ApiErrorSchema = z.object({
  error: z.string(),
  message: z.string(),
  detail: z.array(z.unknown()).optional(),
});

// ──────────────────────────────────────────────
// Inferred Types (use these instead of manual interfaces)
// ──────────────────────────────────────────────

/** Inferred PlaceSignal type from Zod schema. */
export type PlaceSignalZ = z.infer<typeof PlaceSignalSchema>;

/** Inferred Destination type from Zod schema. */
export type DestinationZ = z.infer<typeof DestinationSchema>;

/** Inferred VibeProfile type from Zod schema. */
export type VibeProfileZ = z.infer<typeof VibeProfileSchema>;

/** Inferred TravelToNext type from Zod schema. */
export type TravelToNextZ = z.infer<typeof TravelToNextSchema>;

/** Inferred Stop type from Zod schema. */
export type StopZ = z.infer<typeof StopSchema>;

/** Inferred DayPlan type from Zod schema. */
export type DayPlanZ = z.infer<typeof DayPlanSchema>;

/** Inferred Itinerary type from Zod schema. */
export type ItineraryZ = z.infer<typeof ItinerarySchema>;

/** Inferred ApiError type from Zod schema. */
export type ApiErrorZ = z.infer<typeof ApiErrorSchema>;
