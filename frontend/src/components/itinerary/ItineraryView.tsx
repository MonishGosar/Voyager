"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  CalendarDays, Link2, RefreshCw, Navigation,
  Map, ArrowLeft, CloudRain, Info, CheckCircle2
} from "lucide-react";

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────
interface TravelToNext { duration: string; mode: string; }
interface Stop {
  time: string; name: string; description: string;
  neighborhood?: string; wheelchair: boolean; vegetarian: boolean;
  stepFree: boolean; cost: string; priceLevel: number;
  streetViewUrl: string; travelToNext?: TravelToNext | null;
  rainy_day_fallback?: string;
}
interface DayPlan { stops: Stop[]; totalCost: string; }
interface Itinerary {
  days: DayPlan[];
  conflicts_resolved: string[];
  total_estimated_cost: number;
  accessibility_notes: string;
}
interface TripMeta {
  destination: string; startDate: string; endDate: string;
  numDays: number; groupType: string; groupSize: number;
  currency: string; budget: string;
}

// ─────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────
function formatDate(dateStr: string) {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  } catch { return dateStr; }
}

function toGoogleCalendarDate(dateStr: string) {
  // Google Calendar format: YYYYMMDD
  return dateStr.replace(/-/g, "");
}

function buildGoogleCalendarUrl(meta: TripMeta, itinerary: Itinerary) {
  const start = toGoogleCalendarDate(meta.startDate);
  const end   = toGoogleCalendarDate(meta.endDate);
  const title = encodeURIComponent(`✈️ Trip to ${meta.destination}`);
  const details = encodeURIComponent(
    `${meta.numDays} days · ${meta.groupType} · Budget: ${meta.currency} ${meta.budget}\n\n` +
    itinerary.days.map((d, i) =>
      `Day ${i + 1}:\n` + d.stops.map(s => `  ${s.time} – ${s.name}`).join("\n")
    ).join("\n\n")
  );
  const location = encodeURIComponent(meta.destination);
  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${start}/${end}&details=${details}&location=${location}`;
}

function buildShareableUrl(itinerary: Itinerary, meta: TripMeta) {
  try {
    const payload = btoa(encodeURIComponent(JSON.stringify({ itinerary, meta })));
    return `${window.location.origin}/itinerary?data=${payload}`;
  } catch { return window.location.href; }
}

// ─────────────────────────────────────────────────────────────
// Leaflet Map — geocodes each stop, numbered markers + polyline
// ─────────────────────────────────────────────────────────────
async function geocodePlace(query: string): Promise<[number, number] | null> {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
    );
    const data = await res.json();
    if (!data[0]) return null;
    return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
  } catch { return null; }
}

function ItineraryMap({ destination, stops, dayIndex }: { destination: string; stops: Stop[]; dayIndex: number }) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const leafletLoadedRef = useRef(false);

  const initMap = async () => {
    const L = (window as any).L;
    if (!L || !mapRef.current) return;

    // Destroy previous instance on day change
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const map = L.map(mapRef.current, { zoomControl: true, scrollWheelZoom: false });
    mapInstanceRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    // Geocode each stop (name + city for better accuracy)
    const coords: [number, number][] = [];
    for (let i = 0; i < stops.length; i++) {
      const query = `${stops[i].name}, ${destination}`;
      const coord = await geocodePlace(query);
      if (coord) coords.push(coord);
    }

    // Fallback: geocode just the city
    if (coords.length === 0) {
      const cityCoord = await geocodePlace(destination);
      if (cityCoord) {
        map.setView(cityCoord, 13);
        const icon = L.divIcon({
          className: "",
          html: `<div style="background:#2563eb;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;color:white;font-size:11px;font-weight:bold;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,.3)">📍</div>`,
          iconSize: [26, 26], iconAnchor: [13, 13],
        });
        L.marker(cityCoord, { icon }).addTo(map).bindPopup(`<b>${destination}</b>`).openPopup();
      }
      return;
    }

    // Draw polyline route
    if (coords.length > 1) {
      L.polyline(coords, { color: "#2563eb", weight: 3, opacity: 0.6, dashArray: "6 4" }).addTo(map);
    }

    // Add numbered markers for each stop
    coords.forEach((coord, i) => {
      const icon = L.divIcon({
        className: "",
        html: `<div style="background:#2563eb;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;font-weight:700;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,.35);flex-shrink:0">${i + 1}</div>`,
        iconSize: [28, 28], iconAnchor: [14, 14],
      });
      L.marker(coord, { icon })
        .addTo(map)
        .bindPopup(`<b>${i + 1}. ${stops[i]?.name || ""}</b><br/><span style="color:#6b7280;font-size:12px">${stops[i]?.time || ""}</span>`);
    });

    // Fit map to all markers
    map.fitBounds(L.latLngBounds(coords), { padding: [32, 32], maxZoom: 15 });
  };

  const loadLeafletAndInit = () => {
    if ((window as any).L) { initMap(); return; }
    if (leafletLoadedRef.current) return;
    leafletLoadedRef.current = true;

    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css"; link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
    const script = document.createElement("script");
    script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
    script.async = true;
    script.onload = () => initMap();
    document.body.appendChild(script);
  };

  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return;
    loadLeafletAndInit();
  // Re-run when day changes to re-draw markers
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dayIndex, destination]);

  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div
      ref={mapRef}
      className="w-full h-[400px] rounded-2xl overflow-hidden border shadow-inner"
      style={{ position: "relative", zIndex: 0 }}
    />
  );
}

// ─────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────
export default function ItineraryView() {
  const [activeDay, setActiveDay] = useState(0);
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [meta, setMeta] = useState<TripMeta | null>(null);
  const [copied, setCopied] = useState(false);
  const [expandedFallback, setExpandedFallback] = useState<number | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Check for shareable link data first
    const sharedData = searchParams.get("data");
    if (sharedData) {
      try {
        const decoded = JSON.parse(decodeURIComponent(atob(sharedData)));
        if (decoded.itinerary) setItinerary(decoded.itinerary);
        if (decoded.meta) setMeta(decoded.meta);
        return;
      } catch { /* fall through to sessionStorage */ }
    }
    // Load from sessionStorage (normal flow)
    try {
      const raw = sessionStorage.getItem("voyager_itinerary");
      const rawMeta = sessionStorage.getItem("voyager_trip_meta");
      if (raw) setItinerary(JSON.parse(raw));
      if (rawMeta) setMeta(JSON.parse(rawMeta));
    } catch { /* ignore */ }
  }, [searchParams]);

  const handleAddToCalendar = () => {
    window.open(buildGoogleCalendarUrl(meta, itinerary), "_blank");
  };

  const handleCopyLink = async () => {
    const url = buildShareableUrl(itinerary, meta);
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      prompt("Copy this shareable link:", url);
    }
  };

  // ── No itinerary yet — redirect to plan ─────────────────────
  if (!itinerary || !meta) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-24 flex flex-col items-center gap-6 text-center">
        <div className="h-16 w-16 rounded-full bg-blue-50 flex items-center justify-center">
          <Map className="h-8 w-8 text-blue-400" />
        </div>
        <div>
          <p className="text-xl font-semibold text-foreground">No itinerary generated yet</p>
          <p className="text-muted-foreground mt-1 text-sm">Go back and fill in your trip details to build a personalised plan.</p>
        </div>
        <button
          onClick={() => router.push("/plan")}
          className="px-8 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors shadow-sm"
        >
          Plan my trip
        </button>
      </div>
    );
  }

  const currentDay = itinerary.days[activeDay];

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 animate-fade-up">
      <button
        onClick={() => router.push("/plan")}
        className="mb-6 flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to trip details
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-8">
        {/* ── Left: itinerary ───────────────────────────── */}
        <div className="space-y-6">
          {/* Header card */}
          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl shadow-lg p-6 relative overflow-hidden text-white">
            <div className="absolute right-0 top-0 w-48 h-48 bg-white/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
            <div className="flex items-center justify-between relative z-10">
              <div>
                <h2 className="font-display text-3xl font-semibold tracking-tight">{meta.destination}</h2>
                <p className="text-blue-200 mt-1 font-medium text-sm">
                  {formatDate(meta.startDate)} – {formatDate(meta.endDate)} · {meta.numDays ?? itinerary.days.length} days
                </p>
                <p className="text-blue-200 text-xs mt-0.5 capitalize">
                  {meta.groupType} · {meta.groupSize} {meta.groupSize === 1 ? "person" : "people"}
                </p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-mono font-bold">
                  {meta.currency === "EUR" ? "€" : meta.currency === "USD" ? "$" : meta.currency === "GBP" ? "£" : "₹"}
                  {itinerary.total_estimated_cost.toLocaleString()}
                </p>
                <p className="text-xs text-blue-200 font-medium mt-1">estimated total</p>
              </div>
            </div>
          </div>

          {/* Conflict resolutions */}
          {itinerary.conflicts_resolved.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 shadow-sm">
              <h4 className="text-amber-900 font-semibold mb-3 flex items-center gap-2 text-sm">
                <SparklesIcon className="h-4 w-4 text-amber-600" />
                How we resolved your constraints
              </h4>
              <ul className="space-y-1.5 text-sm text-amber-800">
                {itinerary.conflicts_resolved.map((c, i) => (
                  <li key={i} className="flex gap-2"><span className="text-amber-500 shrink-0">•</span>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Day tabs */}
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {itinerary.days.map((_, i) => (
              <button
                key={i}
                onClick={() => { setActiveDay(i); setExpandedFallback(null); }}
                className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all shrink-0 ${
                  activeDay === i
                    ? "bg-blue-600 text-white shadow-md ring-2 ring-blue-600/20"
                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
                }`}
              >
                Day {i + 1}
              </button>
            ))}
          </div>

          {/* Stops */}
          <div className="space-y-4 mt-2">
            {itinerary.days[activeDay]?.stops.map((stop, j) => (
              <div key={j} className="bg-card text-card-foreground border rounded-2xl shadow-sm hover:shadow-md transition-shadow p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex gap-4 flex-1">
                    <span className="font-mono text-sm font-semibold text-muted-foreground shrink-0 pt-0.5 w-16 tabular-nums">
                      {stop.time}
                    </span>
                    <div className="space-y-2 flex-1">
                      <div>
                        <p className="font-semibold text-lg leading-tight text-foreground">{stop.name}</p>
                        {stop.neighborhood && (
                          <p className="text-xs text-muted-foreground/70 mt-0.5 font-medium uppercase tracking-wide">{stop.neighborhood}</p>
                        )}
                        <p className="text-sm text-muted-foreground mt-1">{stop.description}</p>
                      </div>
                      <div className="flex gap-2 flex-wrap pt-1">
                        {stop.wheelchair && (
                          <span className="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-full font-medium bg-green-50 text-green-700 border border-green-200">
                            ♿ Accessible
                          </span>
                        )}
                        {stop.vegetarian && (
                          <span className="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-full font-medium bg-green-50 text-green-700 border border-green-200">
                            🌿 Veg options
                          </span>
                        )}
                      </div>

                      {/* Rainy day fallback */}
                      {stop.rainy_day_fallback && (
                        <div>
                          <button
                            onClick={() => setExpandedFallback(expandedFallback === j ? null : j)}
                            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors pt-1"
                          >
                            <CloudRain className="h-3.5 w-3.5" />
                            Rainy day alternative
                          </button>
                          {expandedFallback === j && (
                            <p className="text-xs text-muted-foreground mt-1.5 pl-5 border-l-2 border-blue-200">
                              {stop.rainy_day_fallback}
                            </p>
                          )}
                        </div>
                      )}

                      {stop.travelToNext && (
                        <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground pt-3 mt-3 border-t">
                          <Navigation className="h-3.5 w-3.5" />
                          {stop.travelToNext.duration} · {stop.travelToNext.mode}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-mono font-medium">{stop.cost}</p>
                    <div className="flex gap-0.5 mt-1.5 justify-end">
                      {[...Array(4)].map((_, k) => (
                        <span key={k} className={`text-[10px] ${k < stop.priceLevel ? "text-foreground" : "text-muted-foreground/30"}`}>€</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            <div className="flex justify-end pt-2 border-t mt-6">
              <p className="text-sm text-muted-foreground font-medium">
                Day {activeDay + 1} total: <span className="font-mono font-bold text-foreground text-base ml-1">{itinerary.days[activeDay]?.totalCost}</span>
              </p>
            </div>
          </div>
        </div>

        {/* ── Right: Map + Export ───────────────────────── */}
        <div className="hidden lg:block">
          <div className="sticky top-20 space-y-4">
            {/* Interactive Map — re-renders per day with real stop markers */}
            <ItineraryMap
              destination={meta.destination}
              stops={itinerary.days[activeDay]?.stops || []}
              dayIndex={activeDay}
            />

            {/* Export & Share */}
            <div className="bg-card text-card-foreground border rounded-2xl p-5 space-y-3 shadow-sm">
              <h3 className="font-semibold text-sm mb-3">Export &amp; share</h3>
              <button
                onClick={handleAddToCalendar}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                <CalendarDays className="h-4 w-4" />
                Add to Google Calendar
              </button>
              <button
                onClick={handleCopyLink}
                className={`w-full border py-2.5 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  copied
                    ? "bg-green-50 text-green-700 border-green-200"
                    : "hover:bg-accent"
                }`}
              >
                {copied ? (
                  <><CheckCircle2 className="h-4 w-4" /> Copied!</>
                ) : (
                  <><Link2 className="h-4 w-4" /> Copy shareable link</>
                )}
              </button>
              <div className="pt-2">
                <button
                  onClick={() => router.push("/")}
                  className="w-full py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-2"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Trip changed? Re-plan
                </button>
              </div>
            </div>

            {/* Accessibility notes */}
            {itinerary.accessibility_notes && (
              <div className="bg-blue-50 border border-blue-100 rounded-2xl p-4 text-xs text-blue-700 flex gap-2">
                <Info className="h-4 w-4 shrink-0 mt-0.5 text-blue-500" />
                <span>{itinerary.accessibility_notes}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Mobile export buttons ─────────────────────── */}
      <div className="lg:hidden mt-8 space-y-3 border-t pt-6">
        <button
          onClick={handleAddToCalendar}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <CalendarDays className="h-4 w-4" />
          Add to Google Calendar
        </button>
        <button
          onClick={handleCopyLink}
          className={`w-full border py-3 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2 ${
            copied ? "bg-green-50 text-green-700 border-green-200" : "hover:bg-accent"
          }`}
        >
          {copied ? <><CheckCircle2 className="h-4 w-4" /> Copied!</> : <><Link2 className="h-4 w-4" /> Copy shareable link</>}
        </button>
      </div>
    </div>
  );
}

function SparklesIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z" />
    </svg>
  );
}
