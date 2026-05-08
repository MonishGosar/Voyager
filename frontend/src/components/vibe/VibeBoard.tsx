"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, X, ArrowRight, Loader2 } from "lucide-react";

export default function VibeBoard() {
  const [photos, setPhotos] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [destinations, setDestinations] = useState<{name: string, country: string}[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    
    const newFiles = Array.from(e.target.files).slice(0, 6);
    setPhotos(newFiles);
    
    const newPreviews = newFiles.map(f => URL.createObjectURL(f));
    setPreviews(newPreviews);
    
    setLoading(true);
    
    try {
      const formData = new FormData();
      newFiles.forEach(file => formData.append("files", file));
      
      const res = await fetch("http://localhost:8000/api/vibe", {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        const data = await res.json();
        setTags(data.tags || []);
        setDestinations(data.suggested_destinations || []);
      }
    } catch (err) {
      console.error(err);
      setTags(["Error analyzing vibe"]);
    } finally {
      setLoading(false);
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const goToStep2 = () => {
    router.push("/plan");
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 py-12 animate-fade-up">
      <div className="space-y-2">
        <h1 className="font-display text-4xl font-semibold tracking-tight text-foreground">
          What's your travel vibe?
        </h1>
        <p className="text-muted-foreground text-lg">
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
        className="border-2 border-dashed border-border rounded-xl p-16 hover:border-blue-400 hover:bg-blue-50/50 transition-all cursor-pointer group flex items-center justify-center bg-card shadow-sm"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="flex flex-col items-center gap-4 text-center">
          {loading ? (
             <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center">
               <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
             </div>
          ) : previews.length > 0 ? (
             <div className="flex gap-2 justify-center">
               {previews.map((src, i) => (
                 <img key={i} src={src} className="h-16 w-16 object-cover rounded-md shadow-sm" alt="Preview" />
               ))}
             </div>
          ) : (
            <>
              <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-foreground">Click to upload photos</p>
                <p className="text-sm text-muted-foreground mt-1">up to 6 images</p>
              </div>
            </>
          )}
        </div>
      </div>

      {tags.length > 0 && (
        <div className="space-y-4 animate-fade-up" style={{ animationDelay: '100ms' }}>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Detected vibe
          </p>
          <div className="flex flex-wrap gap-2">
            {tags.map(tag => (
              <span 
                key={tag} 
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-secondary hover:bg-destructive/10 hover:text-destructive text-secondary-foreground rounded-full text-sm font-medium transition-colors cursor-pointer border border-transparent hover:border-destructive/20"
                onClick={() => removeTag(tag)}
              >
                {tag}
                <X className="h-3.5 w-3.5" />
              </span>
            ))}
          </div>
        </div>
      )}

      {destinations.length > 0 && (
        <div className="space-y-4 animate-fade-up" style={{ animationDelay: '200ms' }}>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Suggested destinations
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {destinations.map(dest => (
              <button 
                key={dest.name}
                onClick={() => setSelected(dest.name)}
                className={`rounded-xl border p-4 text-left transition-all hover:shadow-md ${selected === dest.name ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500 shadow-sm" : "bg-card hover:border-blue-300"}`}
              >
                <p className="font-semibold text-foreground">{dest.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{dest.country}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      <button 
        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 shadow-sm"
        onClick={goToStep2} 
        disabled={tags.length === 0 || loading}
      >
        Continue to trip details
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  );
}
