"use client";

/**
 * VibeBoard — Mood board photo upload and AI analysis component.
 *
 * This is Step 1 of the Voyager wizard. Users upload 1-6 travel
 * inspiration photos, which are analyzed by Gemini to extract a
 * structured VibeProfile (tags, mood, destinations, style, pace).
 *
 * The extracted vibe profile is persisted in sessionStorage for use
 * in the planning step (ConstraintForm).
 *
 * @example
 * ```tsx
 * <VibeBoard />
 * ```
 */

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, ArrowRight, Loader2 } from "lucide-react";
import type { Destination, VibeProfile } from "@/types";
import { VibeProfileSchema } from "@/lib/schemas";
import { apiUrl } from "@/lib/api";

/** Maximum number of photos that can be uploaded. */
const MAX_PHOTOS = 6;

/** Backend API URL for vibe analysis. */
const VIBE_API_URL = apiUrl("/api/vibe");

export default function VibeBoard(): JSX.Element {
  const [photos, setPhotos] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Send photos to the backend for AI vibe analysis.
   *
   * @param filesToAnalyze - Array of File objects to upload.
   */
  const analyzePhotos = async (filesToAnalyze: File[]): Promise<void> => {
    if (!filesToAnalyze.length) return;
    setLoading(true);
    try {
      const formData = new FormData();
      filesToAnalyze.forEach(file => formData.append("files", file));
      
      const res = await fetch(VIBE_API_URL, {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        const raw: unknown = await res.json();
        const parsed = VibeProfileSchema.safeParse(raw);

        if (parsed.success) {
          const data: VibeProfile = parsed.data;
          setTags(data.tags || []);
          setDestinations(data.suggested_destinations || []);
          try { sessionStorage.setItem("voyager_vibe", JSON.stringify(data)); } catch { /* sessionStorage unavailable */ }
        } else {
          console.error("API contract mismatch:", parsed.error);
          setTags(["Error analyzing vibe"]);
        }
      } else {
        console.error("Vibe API error:", res.status, res.statusText);
        setTags(["Error analyzing vibe"]);
      }
    } catch (err: unknown) {
      console.error("Network error during vibe analysis:", err);
      setTags(["Error analyzing vibe"]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle file input change — store files, generate previews, trigger analysis.
   *
   * @param e - The file input change event.
   */
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
    if (!e.target.files?.length) return;
    
    const newFiles = Array.from(e.target.files).slice(0, MAX_PHOTOS);
    setPhotos(newFiles);
    
    const newPreviews = newFiles.map(f => URL.createObjectURL(f));
    setPreviews(newPreviews);
    
    await analyzePhotos(newFiles);
  };

  /**
   * Remove a tag from the detected aesthetics list.
   *
   * @param tagToRemove - The tag string to remove.
   */
  const removeTag = (tagToRemove: string): void => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  /**
   * Navigate to Step 2 (planning) with the selected destination as a query param.
   */
  const goToStep2 = (): void => {
    router.push(`/plan${selected ? `?destination=${encodeURIComponent(selected)}` : ""}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-12 px-4 animate-fade-up">
      <div className="space-y-2 text-center md:text-left">
        <h1 className="font-display text-4xl md:text-5xl font-semibold tracking-tight text-foreground">
          What's your travel vibe?
        </h1>
        <p className="text-muted-foreground text-lg md:text-xl max-w-2xl">
          Drop photos that inspire your next trip. Our AI reads the mood.
        </p>
      </div>

      <input 
        type="file" 
        multiple 
        accept="image/*" 
        className="hidden" 
        ref={fileInputRef}
        onChange={handleFileSelect}
      />

      <div 
        className={`border-2 border-dashed border-border rounded-2xl transition-all cursor-pointer group flex items-center justify-center bg-card shadow-sm overflow-hidden ${previews.length > 0 ? 'p-6' : 'p-20 hover:border-blue-400 hover:bg-blue-50/50'}`}
        onClick={() => {
          if (previews.length === 0) fileInputRef.current?.click();
        }}
      >
        <div className="flex flex-col items-center gap-4 text-center w-full">
          {loading ? (
             <div className="flex flex-col items-center gap-4 py-12">
               <div className="h-14 w-14 rounded-full bg-blue-50 flex items-center justify-center">
                 <Loader2 className="h-7 w-7 text-blue-600 animate-spin" />
               </div>
               <p className="text-sm font-medium text-muted-foreground animate-pulse">Reading visual aesthetics...</p>
             </div>
          ) : previews.length > 0 ? (
             <div className="w-full space-y-4">
               <div className="flex justify-between items-center mb-2">
                 <p className="text-sm font-medium text-muted-foreground">Your Inspiration Board</p>
                 <div className="flex gap-2">
                   <button 
                     onClick={(e) => { e.stopPropagation(); analyzePhotos(photos); }}
                     className="text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1"
                   >
                     Retry Analysis
                   </button>
                   <button 
                     onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
                     className="text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full transition-colors"
                   >
                     + Add more photos
                   </button>
                 </div>
               </div>
               <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 w-full">
                 {previews.map((src, i) => (
                   <div key={i} className="aspect-[4/3] rounded-xl overflow-hidden shadow-sm group/img relative">
                     <img src={src} className="w-full h-full object-cover transition-transform duration-500 group-hover/img:scale-105" alt={`Inspiration ${i + 1}`} />
                     <div className="absolute inset-0 bg-black/0 group-hover/img:bg-black/10 transition-colors" />
                   </div>
                 ))}
               </div>
             </div>
          ) : (
            <>
              <div className="h-16 w-16 rounded-full bg-blue-50 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-sm">
                <Upload className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <p className="font-semibold text-foreground text-lg">Click to upload photos</p>
                <p className="text-sm text-muted-foreground mt-1">Accepts JPG, PNG, WEBP (up to {MAX_PHOTOS} images)</p>
              </div>
            </>
          )}
        </div>
      </div>

      {tags.length > 0 && (
        <div className="space-y-4 animate-fade-up" style={{ animationDelay: '100ms' }}>
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            Detected aesthetic
          </p>
          <div className="flex flex-wrap gap-2.5">
            {tags.map(tag => (
              <span 
                key={tag} 
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-secondary hover:bg-destructive/10 hover:text-destructive text-secondary-foreground rounded-full text-sm font-medium transition-colors cursor-pointer border border-transparent hover:border-destructive/20 shadow-sm"
                onClick={() => removeTag(tag)}
              >
                {tag}
                <X className="h-4 w-4 opacity-70" />
              </span>
            ))}
          </div>
        </div>
      )}

      {destinations.length > 0 && (
        <div className="space-y-4 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            AI matched destinations
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {destinations.map(dest => (
              <button 
                key={dest.name}
                onClick={() => setSelected(dest.name)}
                className={`rounded-2xl border p-5 text-left transition-all duration-200 hover:shadow-md ${selected === dest.name ? "border-blue-500 bg-blue-50/80 ring-2 ring-blue-500/20 shadow-md transform -translate-y-1" : "bg-card hover:border-blue-300"}`}
              >
                <p className="font-semibold text-lg text-foreground">{dest.name}</p>
                <p className="text-sm text-muted-foreground mt-1">{dest.country}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="pt-6 border-t flex justify-end">
        <button 
          className="w-full sm:w-auto px-8 bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg"
          onClick={goToStep2} 
          disabled={tags.length === 0 || loading || !selected}
        >
          {selected ? `Continue with ${selected}` : "Continue to trip details"}
          <ArrowRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
