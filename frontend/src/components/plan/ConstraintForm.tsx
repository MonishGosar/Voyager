"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Calendar as CalendarIcon, MapPin, Users, Coins, ArrowLeft } from "lucide-react";

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
        <div className="bg-card text-card-foreground shadow-2xl w-96 p-10 space-y-8 rounded-3xl border border-blue-100">
          <div className="space-y-2 text-center">
            <p className="font-display text-2xl font-semibold text-blue-950">Building itinerary</p>
            <p className="text-sm text-muted-foreground">This takes about 15 seconds</p>
          </div>
          <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-blue-600 w-1/2 animate-pulse" />
          </div>
          <div className="space-y-3 text-sm text-muted-foreground text-center">
            <p>Reading your travel vibe...</p>
            <p className="text-blue-600 font-medium">Resolving budget constraints...</p>
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

      <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
        <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-lg text-foreground">Where & when</h3>
        </div>
        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Destination</label>
            <input 
              className="flex h-12 w-full rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" 
              value={destination}
              onChange={e => setDestination(e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Start Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
                <input type="date" className="flex h-12 w-full rounded-xl border border-input bg-transparent pl-12 pr-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">End Date</label>
              <div className="relative">
                <CalendarIcon className="absolute left-4 top-3.5 h-5 w-5 text-muted-foreground" />
                <input type="date" className="flex h-12 w-full rounded-xl border border-input bg-transparent pl-12 pr-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-lg text-foreground">Group</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex flex-wrap gap-3">
                {['Solo', 'Couple', 'Friends', 'Family'].map(type => (
                  <button key={type} className="px-5 py-2.5 rounded-full border text-sm font-medium hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 transition-colors">
                    {type}
                  </button>
                ))}
            </div>
          </div>
        </div>

        <div className="bg-card text-card-foreground border rounded-2xl shadow-sm overflow-hidden">
          <div className="p-6 border-b bg-muted/30 flex items-center gap-2">
            <Coins className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-lg text-foreground">Budget & style</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Total budget</label>
              <div className="flex gap-3">
                <select className="h-12 rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 w-28">
                  <option>USD $</option>
                  <option>EUR €</option>
                  <option>INR ₹</option>
                </select>
                <input 
                  type="number"
                  className="flex-1 h-12 rounded-xl border border-input bg-transparent px-4 py-2 text-base shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600" 
                  value={budget}
                  onChange={e => setBudget(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-8 border-t flex flex-col sm:flex-row justify-between items-center gap-4">
        <button 
          className="w-full sm:w-auto px-6 py-4 rounded-xl font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition-colors flex items-center justify-center gap-2"
          onClick={() => router.push("/")}
        >
          <ArrowLeft className="h-5 w-5" />
          Back to Vibe Board
        </button>
        <button 
          className="w-full sm:w-auto px-10 bg-blue-600 text-white hover:bg-blue-700 py-4 rounded-xl font-medium shadow-md flex items-center justify-center gap-2 transition-all hover:shadow-lg hover:-translate-y-0.5"
          onClick={buildItinerary}
        >
          Build my itinerary
          <Sparkles className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

