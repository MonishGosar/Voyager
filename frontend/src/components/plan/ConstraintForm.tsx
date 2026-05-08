"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Calendar as CalendarIcon, MapPin, Users, Coins } from "lucide-react";

export default function ConstraintForm() {
  const router = useRouter();
  const [destination, setDestination] = useState("Lisbon");
  const [budget, setBudget] = useState("50000");
  const [loading, setLoading] = useState(false);

  const buildItinerary = () => {
    setLoading(true);
    setTimeout(() => {
      router.push("/itinerary");
    }, 2000);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
        <div className="bg-card text-card-foreground shadow-lg w-80 p-8 space-y-6 rounded-2xl border">
          <div className="space-y-1 text-center">
            <p className="font-display text-xl font-semibold">Building itinerary</p>
            <p className="text-sm text-muted-foreground">This takes about 15 seconds</p>
          </div>
          <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-blue-600 w-1/2 animate-pulse" />
          </div>
          <div className="space-y-2 text-sm text-muted-foreground text-center">
            <p>Reading your travel vibe...</p>
            <p className="text-blue-600 font-medium">Resolving budget constraints...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 py-8 animate-fade-up">
      <div className="space-y-2 mb-8">
        <h2 className="text-3xl font-display font-semibold tracking-tight">Plan your trip</h2>
        <p className="text-muted-foreground text-lg">Tell us the details — we'll handle the conflicts.</p>
      </div>

      <div className="bg-card text-card-foreground border rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <MapPin className="h-4 w-4 text-muted-foreground" />
          <h3 className="font-semibold text-base">Where & when</h3>
        </div>
        <div className="p-6 space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-medium">Destination</label>
            <input 
              className="flex h-11 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" 
              value={destination}
              onChange={e => setDestination(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Start Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <input type="date" className="flex h-11 w-full rounded-md border border-input bg-transparent pl-9 pr-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">End Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <input type="date" className="flex h-11 w-full rounded-md border border-input bg-transparent pl-9 pr-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-card text-card-foreground border rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <h3 className="font-semibold text-base">Group</h3>
        </div>
        <div className="p-6 space-y-4">
           <div className="flex flex-wrap gap-2">
              {['Solo', 'Couple', 'Friends', 'Family'].map(type => (
                <button key={type} className="px-4 py-2 rounded-full border text-sm font-medium hover:bg-accent transition-colors">
                  {type}
                </button>
              ))}
           </div>
        </div>
      </div>

      <div className="bg-card text-card-foreground border rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <Coins className="h-4 w-4 text-muted-foreground" />
          <h3 className="font-semibold text-base">Budget & style</h3>
        </div>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Total budget</label>
            <div className="flex gap-2">
              <select className="h-11 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 w-24">
                <option>USD $</option>
                <option>EUR €</option>
                <option>INR ₹</option>
              </select>
              <input 
                type="number"
                className="flex-1 h-11 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" 
                value={budget}
                onChange={e => setBudget(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      <button 
        className="w-full bg-blue-600 text-white hover:bg-blue-700 py-4 rounded-xl font-medium shadow-md flex items-center justify-center gap-2 transition-all hover:shadow-lg"
        onClick={buildItinerary}
      >
        Build my itinerary
        <Sparkles className="h-4 w-4" />
      </button>
    </div>
  );
}

