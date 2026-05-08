import ItineraryView from "@/components/itinerary/ItineraryView";
import { Compass, ChevronRight } from "lucide-react";

export default function ItineraryPage() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b bg-background/95 backdrop-blur sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="h-6 w-6 text-foreground" />
            <span className="font-display text-xl font-semibold tracking-tight">Voyager</span>
          </div>
          
          <div className="hidden md:flex items-center gap-2 text-sm font-medium">
            <div className="flex items-center gap-1.5 px-3 py-1 text-muted-foreground">
              <span className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-xs">1</span>
              Vibe
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-1.5 px-3 py-1 text-muted-foreground">
              <span className="h-5 w-5 rounded-full bg-muted flex items-center justify-center text-xs">2</span>
              Plan
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <div className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 rounded-full">
              <span className="h-5 w-5 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">3</span>
              Itinerary
            </div>
          </div>
        </div>
      </header>
      <ItineraryView />
    </main>
  );
}

