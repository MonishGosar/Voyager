"use client";

import { useState } from "react";
import { CalendarDays, Link2, RefreshCw, Navigation, Map } from "lucide-react";

export default function ItineraryView() {
  const [activeDay, setActiveDay] = useState(0);

  const itinerary = {
    destination: "Lisbon",
    startDate: "Oct 10",
    endDate: "Oct 14",
    days: 5,
    totalCost: "€1,250",
    conflicts: [
      "Swapped Alfama stairs for step-free scenic route to Miradouro",
      "Kept dinner within €50 per person budget constraint"
    ],
    plan: [
      {
        totalCost: "€85",
        stops: [
          {
            time: "10:00 AM",
            name: "Praça do Comércio",
            description: "Start the day at Lisbon's iconic waterfront square.",
            cost: "Free",
            priceLevel: 0,
            wheelchair: true,
            vegetarian: false,
            stepFree: true,
            travelToNext: { duration: "12 min", mode: "Walk" }
          },
          {
            time: "12:30 PM",
            name: "Time Out Market",
            description: "Lunch at the famous food hall with diverse options.",
            cost: "€25",
            priceLevel: 2,
            wheelchair: true,
            vegetarian: true,
            stepFree: true,
            travelToNext: null
          }
        ]
      }
    ]
  };

  return (
    <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-8 py-8 animate-fade-up">
      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-2xl shadow-sm p-6 relative overflow-hidden">
          <div className="absolute right-0 top-0 w-32 h-32 bg-blue-100 rounded-full blur-3xl opacity-50 -mr-10 -mt-10 pointer-events-none"></div>
          <div className="flex items-center justify-between relative z-10">
            <div>
              <h2 className="font-display text-3xl font-semibold text-blue-950 tracking-tight">{itinerary.destination}</h2>
              <p className="text-sm text-blue-700 mt-1 font-medium">{itinerary.startDate} – {itinerary.endDate} · {itinerary.days} days</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-mono font-semibold text-blue-900">{itinerary.totalCost}</p>
              <p className="text-xs text-blue-700 font-medium mt-1">estimated total</p>
            </div>
          </div>
        </div>

        {itinerary.conflicts.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 shadow-sm">
            <h4 className="text-amber-900 font-semibold mb-3 flex items-center gap-2">
              <SparklesIcon className="h-5 w-5 text-amber-600" />
              How we resolved your constraints
            </h4>
            <ul className="space-y-2 text-sm text-amber-800 font-medium">
              {itinerary.conflicts.map((c, i) => <li key={i} className="flex gap-2"><span className="text-amber-500">•</span> {c}</li>)}
            </ul>
          </div>
        )}

        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {[...Array(itinerary.days)].map((_, i) => (
            <button 
              key={i} 
              onClick={() => setActiveDay(i)}
              className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all shrink-0 ${activeDay === i ? 'bg-foreground text-background shadow-md' : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground'}`}
            >
              Day {i + 1}
            </button>
          ))}
        </div>

        <div className="space-y-4 mt-2">
          {itinerary.plan[0]?.stops.map((stop, j) => (
            <div key={j} className="bg-card text-card-foreground border rounded-2xl shadow-sm hover:shadow-md transition-shadow p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex gap-4">
                  <span className="font-mono text-sm font-semibold text-muted-foreground shrink-0 pt-0.5 w-16">
                    {stop.time}
                  </span>
                  <div className="space-y-2">
                    <div>
                      <p className="font-semibold text-lg leading-tight text-foreground">{stop.name}</p>
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
                      <span key={k} className={`text-[10px] ${k < stop.priceLevel ? 'text-foreground' : 'text-muted-foreground/30'}`}>€</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          <div className="flex justify-end pt-2 border-t mt-6">
            <p className="text-sm text-muted-foreground font-medium">
              Day 1 total: <span className="font-mono font-bold text-foreground text-base ml-1">{itinerary.plan[0]?.totalCost}</span>
            </p>
          </div>
        </div>
      </div>

      <div className="hidden lg:block">
        <div className="sticky top-20 space-y-4">
          <div className="rounded-2xl bg-muted h-[400px] border flex flex-col items-center justify-center gap-3 relative overflow-hidden shadow-inner group">
             <Map className="h-10 w-10 text-muted-foreground/50 group-hover:scale-110 transition-transform duration-300" />
             <p className="text-muted-foreground text-sm font-medium z-10">Interactive Map View</p>
             <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-100/20 via-background/0 to-background/0 pointer-events-none"></div>
          </div>
          
          <div className="bg-card text-card-foreground border rounded-2xl p-5 space-y-3 shadow-sm">
            <h3 className="font-semibold text-sm mb-3">Export & share</h3>
            <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2.5 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2">
              <CalendarDays className="h-4 w-4" />
              Add to Google Calendar
            </button>
            <button className="w-full border py-2.5 rounded-xl text-sm font-medium hover:bg-accent transition-colors flex items-center justify-center gap-2">
              <Link2 className="h-4 w-4" />
              Copy shareable link
            </button>
            <div className="pt-2">
              <button className="w-full py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-2">
                <RefreshCw className="h-3.5 w-3.5" />
                Trip changed? Re-plan
              </button>
            </div>
          </div>
        </div>
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

