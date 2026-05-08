"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, ArrowRight, Loader2, AlertCircle, RefreshCw, ImageIcon } from "lucide-react";
import type { Destination, VibeProfile } from "@/types";
import { VibeProfileSchema } from "@/lib/schemas";
import { apiUrl } from "@/lib/api";

const MAX_PHOTOS = 6;
const VIBE_API_URL = apiUrl("/api/vibe");

function isErrorDestination(dest: Destination): boolean {
  return (
    dest.name === "Error" ||
    dest.country.includes("UNIMPLEMENTED") ||
    dest.country.includes("error") ||
    dest.country.startsWith("{") ||
    /^\d{3}/.test(dest.country)
  );
}

export default function VibeBoard(): JSX.Element {
  const [photos, setPhotos] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const analyzePhotos = async (filesToAnalyze: File[]): Promise<void> => {
    if (!filesToAnalyze.length) return;
    setLoading(true);
    setAnalysisError(null);
    try {
      const formData = new FormData();
      filesToAnalyze.forEach(file => formData.append("files", file));

      const res = await fetch(VIBE_API_URL, { method: "POST", body: formData });

      if (res.ok) {
        const raw: unknown = await res.json();
        const parsed = VibeProfileSchema.safeParse(raw);
        if (parsed.success) {
          const data: VibeProfile = parsed.data;
          const validDests = (data.suggested_destinations || []).filter(d => !isErrorDestination(d));
          const hasApiError = (data.suggested_destinations || []).some(isErrorDestination);

          setTags(data.tags || []);
          setDestinations(validDests);

          if (hasApiError && validDests.length === 0) {
            setAnalysisError("AI model unavailable — destinations couldn't be generated. You can still continue manually.");
          }

          try { sessionStorage.setItem("voyager_vibe", JSON.stringify({ ...data, suggested_destinations: validDests })); } catch { /* ignore */ }
        } else {
          setAnalysisError("Unexpected response from server. Try again.");
        }
      } else {
        setAnalysisError(`Analysis failed (${res.status}). Check API key config and retry.`);
      }
    } catch {
      setAnalysisError("Network error — couldn't reach the analysis server.");
    } finally {
      setLoading(false);
    }
  };

  const handleFiles = async (files: FileList | File[]): Promise<void> => {
    const newFiles = Array.from(files).slice(0, MAX_PHOTOS);
    if (!newFiles.length) return;
    setPhotos(newFiles);
    setPreviews(newFiles.map(f => URL.createObjectURL(f)));
    await analyzePhotos(newFiles);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
    if (e.target.files?.length) await handleFiles(e.target.files);
  };

  const handleDrop = async (e: React.DragEvent): Promise<void> => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.length) await handleFiles(e.dataTransfer.files);
  };

  const removeTag = (tagToRemove: string): void => {
    setTags(tags.filter(t => t !== tagToRemove));
  };

  const goToStep2 = (): void => {
    router.push(`/plan${selected ? `?destination=${encodeURIComponent(selected)}` : ""}`);
  };

  const validTags = tags.filter(t => !t.toLowerCase().includes("error"));

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

      <input type="file" multiple accept="image/*" className="hidden" ref={fileInputRef} onChange={handleFileSelect} />

      {/* Upload zone */}
      <div
        className={`border-2 border-dashed rounded-2xl transition-all duration-200 cursor-pointer group flex items-center justify-center bg-card shadow-sm overflow-hidden
          ${isDragging ? "border-blue-500 bg-blue-50/60 scale-[1.01]" : previews.length > 0 ? "border-border p-6" : "border-border p-20 hover:border-blue-400 hover:bg-blue-50/40"}`}
        onClick={() => { if (previews.length === 0) fileInputRef.current?.click(); }}
        onDragOver={e => { e.preventDefault(); setIsDragging(true); }}
        onDragEnter={() => setIsDragging(true)}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center gap-4 text-center w-full">
          {loading ? (
            <div className="flex flex-col items-center gap-5 py-12">
              <div className="relative h-16 w-16">
                <div className="absolute inset-0 rounded-full bg-blue-100 animate-ping opacity-40" />
                <div className="relative h-16 w-16 rounded-full bg-blue-50 flex items-center justify-center shadow-sm">
                  <Loader2 className="h-7 w-7 text-blue-600 animate-spin" />
                </div>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-foreground">Reading your visual aesthetic…</p>
                <p className="text-xs text-muted-foreground">Analysing colours, mood, style</p>
              </div>
            </div>
          ) : previews.length > 0 ? (
            <div className="w-full space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <ImageIcon className="h-4 w-4" />
                  Inspiration board · {previews.length} photo{previews.length !== 1 ? "s" : ""}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={e => { e.stopPropagation(); analyzePhotos(photos); }}
                    className="text-xs font-medium text-muted-foreground hover:text-foreground bg-muted px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
                  >
                    <RefreshCw className="h-3 w-3" /> Re-analyse
                  </button>
                  <button
                    onClick={e => { e.stopPropagation(); fileInputRef.current?.click(); }}
                    className="text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 px-3 py-1.5 rounded-full transition-colors"
                  >
                    + Add photos
                  </button>
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 w-full">
                {previews.map((src, i) => (
                  <div key={i} className="aspect-[4/3] rounded-xl overflow-hidden shadow-sm group/img relative">
                    <img src={src} className="w-full h-full object-cover transition-transform duration-500 group-hover/img:scale-105" alt={`Inspiration ${i + 1}`} />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover/img:opacity-100 transition-opacity" />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-sm border border-blue-100">
                <Upload className="h-7 w-7 text-blue-600" />
              </div>
              <div>
                <p className="font-semibold text-foreground text-lg">Drop photos or click to upload</p>
                <p className="text-sm text-muted-foreground mt-1">JPG, PNG, WEBP — up to {MAX_PHOTOS} images</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Analysis error banner */}
      {analysisError && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 animate-fade-up">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5 text-amber-600" />
          <span>{analysisError}</span>
        </div>
      )}

      {/* Tags */}
      {validTags.length > 0 && (
        <div className="space-y-3 animate-fade-up" style={{ animationDelay: "100ms" }}>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">Detected aesthetic</p>
          <div className="flex flex-wrap gap-2">
            {validTags.map(tag => (
              <span
                key={tag}
                onClick={() => removeTag(tag)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-secondary hover:bg-destructive/10 hover:text-destructive text-secondary-foreground rounded-full text-sm font-medium transition-colors cursor-pointer border border-transparent hover:border-destructive/20"
              >
                {tag}
                <X className="h-3.5 w-3.5 opacity-60" />
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Destinations */}
      {destinations.length > 0 && (
        <div className="space-y-3 animate-fade-up" style={{ animationDelay: "200ms" }}>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">AI matched destinations</p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {destinations.map(dest => (
              <button
                key={dest.name}
                onClick={() => setSelected(dest.name === selected ? "" : dest.name)}
                className={`rounded-2xl border p-5 text-left transition-all duration-200 group relative overflow-hidden
                  ${selected === dest.name
                    ? "border-blue-500 bg-blue-50/80 ring-2 ring-blue-500/20 shadow-md -translate-y-0.5"
                    : "bg-card hover:border-blue-200 hover:shadow-md hover:-translate-y-0.5"
                  }`}
              >
                <div className={`absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 transition-opacity ${selected === dest.name ? "opacity-100" : "group-hover:opacity-100"}`} />
                <p className="font-semibold text-base text-foreground relative">{dest.name}</p>
                <p className="text-sm text-muted-foreground mt-0.5 relative">{dest.country}</p>
                {selected === dest.name && (
                  <span className="absolute top-3 right-3 h-5 w-5 rounded-full bg-blue-600 flex items-center justify-center">
                    <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="pt-6 border-t flex flex-col sm:flex-row justify-between items-center gap-4">
        {previews.length === 0 ? (
          <p className="text-sm text-muted-foreground">Upload photos to detect your vibe</p>
        ) : !selected && destinations.length > 0 ? (
          <p className="text-sm text-muted-foreground">Pick a destination to continue</p>
        ) : (
          <div />
        )}
        <button
          className="w-full sm:w-auto px-8 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white py-4 rounded-xl font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:hover:translate-y-0"
          onClick={goToStep2}
          disabled={(validTags.length === 0 && destinations.length === 0) || loading || (destinations.length > 0 && !selected)}
        >
          {selected ? `Continue with ${selected}` : "Continue to trip details"}
          <ArrowRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
