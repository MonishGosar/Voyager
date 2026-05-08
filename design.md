# 🎨 TripMind Voyager — Design System (v2)
> Next.js 14 + shadcn/ui + Tailwind CSS
> Aesthetic: Clean, minimal, professional — Google-grade product design

---

## Design Philosophy

**"The best travel tool should feel as reliable as Google Maps and as inspiring as a travel magazine."**

Forget dark navy + amber dramatic themes. We're going **light, clean, precise** — Google Search / Google Flights / Linear aesthetic. White backgrounds, subtle grays, a single brand accent, and typography that breathes. The intelligence shows through clarity, not decoration.

The judges are evaluating Code Quality and Accessibility — a clean, minimal, professional interface signals engineering maturity far more than a flashy dark theme.

---

## shadcn/ui Setup

```bash
# Initialize shadcn in Next.js project
npx shadcn@latest init

# Answer prompts:
# Style: Default
# Base color: Zinc
# CSS variables: Yes

# Install all components we'll use
npx shadcn@latest add card badge button tabs dialog progress \
  separator skeleton toggle calendar popover slider \
  input label textarea select checkbox alert tooltip \
  sheet command combobox
```

`components.json`:
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

---

## Color System (CSS Variables — shadcn default + brand)

```css
/* src/app/globals.css */
@layer base {
  :root {
    /* shadcn defaults (Zinc base) */
    --background:         0 0% 100%;          /* pure white */
    --foreground:         240 10% 3.9%;       /* near black */
    --card:               0 0% 100%;
    --card-foreground:    240 10% 3.9%;
    --popover:            0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary:            240 5.9% 10%;       /* dark ink */
    --primary-foreground: 0 0% 98%;
    --secondary:          240 4.8% 95.9%;     /* light gray */
    --secondary-foreground: 240 5.9% 10%;
    --muted:              240 4.8% 95.9%;
    --muted-foreground:   240 3.8% 46.1%;     /* medium gray */
    --accent:             240 4.8% 95.9%;
    --accent-foreground:  240 5.9% 10%;
    --destructive:        0 84.2% 60.2%;
    --border:             240 5.9% 90%;       /* subtle borders */
    --input:              240 5.9% 90%;
    --ring:               240 5.9% 10%;
    --radius:             0.5rem;

    /* Brand additions */
    --brand:              217 91% 60%;        /* Google Blue #3B82F6 */
    --brand-light:        213 100% 96%;       /* light blue tint */
    --brand-foreground:   0 0% 100%;

    --success:            142 76% 36%;        /* green */
    --success-light:      138 76% 97%;
    --warning:            38 92% 50%;         /* amber */
    --warning-light:      48 100% 96%;

    /* Accessibility badge colors */
    --a11y:               142 72% 29%;
    --a11y-bg:            138 76% 97%;
  }

  .dark {
    --background:         240 10% 3.9%;
    --foreground:         0 0% 98%;
    /* ... dark mode tokens if needed */
  }
}
```

**Color usage rules:**
- Background: always `hsl(var(--background))` — white
- Borders: `hsl(var(--border))` — use liberally, they define structure
- Text hierarchy: `foreground` → `muted-foreground` → placeholder
- Brand blue: only for primary CTAs, active states, links
- Never use color to convey meaning alone — always pair with icon or label

---

## Typography

```css
/* next/font — loaded in app/layout.tsx */
import { Inter } from 'next/font/google'
import { Fraunces } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
  weight: ['400', '600'],
  style: ['normal', 'italic'],
})
```

```css
/* tailwind.config.ts */
fontFamily: {
  sans:    ['var(--font-sans)', 'system-ui', 'sans-serif'],
  display: ['var(--font-display)', 'Georgia', 'serif'],
  mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
}
```

**Usage:**
- `font-display` — hero text, destination names, day headings (Fraunces: editorial, warm)
- `font-sans` — everything else (Inter: clean, neutral, Google-like)
- `font-mono` — times, coordinates, cost numbers

**Type scale (Tailwind):**
```
text-xs   (12px) — badges, captions, meta
text-sm   (14px) — secondary content, form labels
text-base (16px) — body copy
text-lg   (18px) — card titles, section intros
text-xl   (20px) — page section headers
text-2xl  (24px) — page titles
text-4xl  (36px) — hero headline (font-display)
```

---

## Spacing & Layout

```
App Shell:
┌─────────────────────────────────────────────────┐
│  Header (56px) — logo + stepper + theme toggle  │
├─────────────────────────────────────────────────┤
│                                                 │
│  Main content (max-w-5xl mx-auto px-6)          │
│  - Step 1: VibeBoard (centered, max-w-2xl)      │
│  - Step 2: ConstraintForm (max-w-2xl)           │
│  - Step 3: ItineraryView (full width grid)      │
│                                                 │
└─────────────────────────────────────────────────┘

Spacing unit: Tailwind 4px base
Container: max-w-5xl (1024px) with mx-auto
Section gap: space-y-8
Card padding: p-6
Inner gap: space-y-4 or space-y-6
Border radius: rounded-xl (cards), rounded-md (inputs), rounded-full (badges)
```

---

## Component Specifications

### 1. Header / Stepper

```tsx
// Clean Google-style progress stepper
<header className="border-b bg-background/95 backdrop-blur sticky top-0 z-50">
  <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
    
    {/* Logo */}
    <div className="flex items-center gap-2">
      <MapPin className="h-5 w-5 text-blue-500" />
      <span className="font-display text-lg font-semibold">TripMind Voyager</span>
    </div>

    {/* Steps — shadcn-style pills */}
    <div className="flex items-center gap-1 text-sm">
      <StepPill number={1} label="Vibe" active={step === 1} done={step > 1} />
      <ChevronRight className="h-4 w-4 text-muted-foreground" />
      <StepPill number={2} label="Plan" active={step === 2} done={step > 2} />
      <ChevronRight className="h-4 w-4 text-muted-foreground" />
      <StepPill number={3} label="Itinerary" active={step === 3} done={false} />
    </div>

    <ThemeToggle />
  </div>
</header>
```

---

### 2. VibeBoard (Step 1)

```tsx
// Clean, minimal upload zone
<div className="max-w-2xl mx-auto space-y-8 py-12">
  
  {/* Hero text */}
  <div className="space-y-2">
    <h1 className="font-display text-4xl font-semibold tracking-tight">
      What's your travel vibe?
    </h1>
    <p className="text-muted-foreground text-lg">
      Drop photos that inspire your next trip. Our AI reads the mood.
    </p>
  </div>

  {/* Upload zone */}
  <div className="border-2 border-dashed border-border rounded-xl p-12
                  hover:border-blue-400 hover:bg-blue-50/50 transition-colors
                  cursor-pointer group">
    <div className="flex flex-col items-center gap-3 text-center">
      <Upload className="h-8 w-8 text-muted-foreground group-hover:text-blue-500 transition-colors" />
      <div>
        <p className="font-medium">Drop photos here</p>
        <p className="text-sm text-muted-foreground">or click to browse · up to 6 photos</p>
      </div>
    </div>
  </div>

  {/* Uploaded thumbnails */}
  <div className="grid grid-cols-3 gap-3">
    {photos.map((photo, i) => (
      <div key={i} className="relative aspect-square rounded-lg overflow-hidden bg-muted">
        <Image src={photo.url} alt={photo.vibeDescription} fill className="object-cover" />
        <button className="absolute top-1 right-1 rounded-full bg-background/80 p-1">
          <X className="h-3 w-3" />
        </button>
      </div>
    ))}
  </div>

  {/* Vibe tags — shadcn Badge */}
  {tags.length > 0 && (
    <div className="space-y-3">
      <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
        Detected vibe
      </p>
      <div className="flex flex-wrap gap-2">
        {tags.map(tag => (
          <Badge key={tag} variant="secondary" className="cursor-pointer hover:bg-destructive/10">
            {tag}
            <X className="ml-1 h-3 w-3" />
          </Badge>
        ))}
      </div>
    </div>
  )}

  {/* Suggested destinations */}
  {destinations.length > 0 && (
    <div className="space-y-3">
      <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
        Suggested destinations
      </p>
      <div className="grid grid-cols-3 gap-2">
        {destinations.map(dest => (
          <button key={dest.name}
            onClick={() => selectDestination(dest)}
            className={cn(
              "rounded-xl border p-4 text-left transition-colors hover:bg-accent",
              selected === dest.name && "border-blue-500 bg-blue-50"
            )}>
            <p className="font-medium text-sm">{dest.name}</p>
            <p className="text-xs text-muted-foreground">{dest.country}</p>
          </button>
        ))}
      </div>
    </div>
  )}

  <Button size="lg" className="w-full" onClick={goToStep2} disabled={tags.length === 0}>
    Continue to trip details
    <ArrowRight className="ml-2 h-4 w-4" />
  </Button>
</div>
```

---

### 3. ConstraintForm (Step 2)

```tsx
// shadcn Card sections with clean separation
<div className="max-w-2xl mx-auto space-y-6 py-8">

  <div className="space-y-1">
    <h2 className="text-2xl font-display font-semibold">Plan your trip</h2>
    <p className="text-muted-foreground">Tell us the details — we'll handle the conflicts.</p>
  </div>

  {/* Section A: Where & When */}
  <Card>
    <CardHeader className="pb-3">
      <CardTitle className="text-base">Where & when</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="space-y-2">
        <Label>Destination</Label>
        <Combobox placeholder="Search destinations..." value={destination} />
        {vibeDestination && (
          <p className="text-xs text-muted-foreground">
            Suggested from your vibe: <button className="text-blue-500 hover:underline">{vibeDestination}</button>
          </p>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Start date</Label>
          <DatePicker value={startDate} onChange={setStartDate} />
        </div>
        <div className="space-y-2">
          <Label>End date</Label>
          <DatePicker value={endDate} onChange={setEndDate} />
        </div>
      </div>
    </CardContent>
  </Card>

  {/* Section B: Group */}
  <Card>
    <CardHeader className="pb-3">
      <CardTitle className="text-base">Who's coming</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <ToggleGroup type="single" value={groupType} onValueChange={setGroupType}
        className="justify-start gap-2">
        {['Solo', 'Couple', 'Friends', 'Family'].map(type => (
          <ToggleGroupItem key={type} value={type.toLowerCase()}
            className="rounded-full border data-[state=on]:bg-primary data-[state=on]:text-primary-foreground">
            {type}
          </ToggleGroupItem>
        ))}
      </ToggleGroup>
      <div className="flex items-center gap-4">
        <Label>Group size</Label>
        <Input type="number" min={1} max={20} value={groupSize}
          onChange={e => setGroupSize(+e.target.value)}
          className="w-20" />
      </div>
    </CardContent>
  </Card>

  {/* Section C: Budget & Style */}
  <Card>
    <CardHeader className="pb-3">
      <CardTitle className="text-base">Budget & style</CardTitle>
    </CardHeader>
    <CardContent className="space-y-6">
      <div className="space-y-2">
        <Label>Total budget</Label>
        <div className="flex gap-2">
          <Select value={currency} onValueChange={setCurrency}>
            <SelectTrigger className="w-24"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="INR">₹ INR</SelectItem>
              <SelectItem value="USD">$ USD</SelectItem>
              <SelectItem value="EUR">€ EUR</SelectItem>
            </SelectContent>
          </Select>
          <Input type="number" value={budget} onChange={e => setBudget(+e.target.value)}
            placeholder="50000" className="flex-1" />
        </div>
        {budget && days && (
          <p className="text-xs text-muted-foreground">
            ~{formatCurrency(budget / days, currency)} per day
          </p>
        )}
      </div>
      <div className="space-y-3">
        <div className="flex justify-between">
          <Label>Travel pace</Label>
          <span className="text-sm text-muted-foreground">
            {pace < 33 ? 'Slow & relaxed' : pace < 66 ? 'Balanced' : 'Fully packed'}
          </span>
        </div>
        <Slider value={[pace]} onValueChange={([v]) => setPace(v)} max={100} step={1} />
      </div>
    </CardContent>
  </Card>

  {/* Section D: Accessibility — always visible, never hidden */}
  <Card>
    <CardHeader className="pb-3">
      <CardTitle className="text-base">Accessibility & needs</CardTitle>
      <CardDescription>We build these into the itinerary automatically</CardDescription>
    </CardHeader>
    <CardContent className="space-y-3">
      {[
        { id: 'wheelchair', label: 'Wheelchair accessible venues', icon: '♿' },
        { id: 'dietary', label: 'Dietary restrictions', icon: '🌿' },
        { id: 'low_mobility', label: 'Low mobility (minimal stairs)', icon: '🚶' },
        { id: 'sensory', label: 'Sensory considerations', icon: '🔇' },
      ].map(item => (
        <div key={item.id} className="flex items-center gap-3">
          <Checkbox id={item.id} checked={accessibility[item.id]}
            onCheckedChange={v => setAccessibility(prev => ({...prev, [item.id]: v}))} />
          <Label htmlFor={item.id} className="cursor-pointer font-normal">
            <span className="mr-2">{item.icon}</span>{item.label}
          </Label>
        </div>
      ))}
    </CardContent>
  </Card>

  <Button size="lg" className="w-full bg-blue-600 hover:bg-blue-700" onClick={buildItinerary}>
    Build my itinerary
    <Sparkles className="ml-2 h-4 w-4" />
  </Button>
</div>
```

---

### 4. Loading State

```tsx
// Full-page overlay with progress steps — no spinner, narrative loading
<div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
  <Card className="w-80 p-6 space-y-6">
    <div className="space-y-1">
      <p className="font-display text-lg font-semibold">Building your itinerary</p>
      <p className="text-sm text-muted-foreground">This takes about 15 seconds</p>
    </div>
    <Progress value={progress} className="h-1.5" />
    <div className="space-y-2">
      {loadingSteps.map((step, i) => (
        <div key={i} className={cn(
          "flex items-center gap-3 text-sm transition-opacity duration-500",
          i === currentStep ? "opacity-100" : "opacity-40"
        )}>
          {i < currentStep
            ? <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
            : i === currentStep
            ? <Loader2 className="h-4 w-4 text-blue-500 shrink-0 animate-spin" />
            : <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
          }
          {step}
        </div>
      ))}
    </div>
  </Card>
</div>

// Steps text:
const loadingSteps = [
  "Reading your travel vibe...",
  "Resolving budget constraints...",
  "Finding accessible venues...",
  "Checking live hours and ratings...",
  "Calculating optimal routes...",
  "Building your day-by-day plan...",
]
```

---

### 5. ItineraryView (Step 3)

```tsx
// Two-column: day cards left, sticky map right
<div className="grid grid-cols-1 lg:grid-cols-[1fr_420px] gap-6 py-6">
  
  {/* LEFT: Day cards */}
  <div className="space-y-4">
    
    {/* Trip summary header */}
    <Card className="bg-blue-50 border-blue-200">
      <CardContent className="pt-4 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-2xl font-semibold">{destination}</h2>
            <p className="text-sm text-muted-foreground">{startDate} – {endDate} · {days} days</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-mono font-semibold">{totalCost}</p>
            <p className="text-xs text-muted-foreground">estimated total</p>
          </div>
        </div>
      </CardContent>
    </Card>

    {/* Conflict resolution log — shadcn Alert */}
    {conflicts.length > 0 && (
      <Alert className="border-amber-200 bg-amber-50">
        <Lightbulb className="h-4 w-4 text-amber-600" />
        <AlertTitle className="text-amber-900">How we resolved your constraints</AlertTitle>
        <AlertDescription>
          <ul className="mt-1 space-y-1 text-sm text-amber-800">
            {conflicts.map((c, i) => <li key={i}>· {c}</li>)}
          </ul>
        </AlertDescription>
      </Alert>
    )}

    {/* Day tabs */}
    <Tabs value={activeDay} onValueChange={setActiveDay}>
      <TabsList className="w-full justify-start overflow-x-auto">
        {itinerary.days.map((day, i) => (
          <TabsTrigger key={i} value={String(i)} className="shrink-0">
            Day {i + 1}
          </TabsTrigger>
        ))}
      </TabsList>

      {itinerary.days.map((day, i) => (
        <TabsContent key={i} value={String(i)} className="space-y-3 mt-4">
          {day.stops.map((stop, j) => (
            <Card key={j} className="hover:shadow-sm transition-shadow">
              <CardContent className="pt-4 space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex gap-3">
                    {/* Time */}
                    <span className="font-mono text-sm text-muted-foreground shrink-0 pt-0.5">
                      {stop.time}
                    </span>
                    <div className="space-y-1">
                      <p className="font-medium leading-tight">{stop.name}</p>
                      <p className="text-sm text-muted-foreground">{stop.description}</p>
                      {/* Accessibility badges */}
                      <div className="flex gap-1.5 flex-wrap">
                        {stop.wheelchair && <AccessibilityBadge type="wheelchair" />}
                        {stop.vegetarian && <AccessibilityBadge type="dietary" />}
                        {stop.stepFree && <AccessibilityBadge type="stepFree" />}
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-mono">{stop.cost}</p>
                    <div className="flex gap-0.5 mt-1">
                      {Array(stop.priceLevel).fill(null).map((_, k) =>
                        <span key={k} className="text-xs text-muted-foreground">€</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Street View preview */}
                <button onClick={() => openStreetView(stop)}
                  className="w-full rounded-lg overflow-hidden aspect-video relative bg-muted
                             hover:ring-2 hover:ring-blue-400 transition-all">
                  <Image src={stop.streetViewUrl} alt={`Street view of ${stop.name}`}
                    fill className="object-cover" />
                  <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors
                                  flex items-center justify-center opacity-0 hover:opacity-100">
                    <span className="text-white text-sm font-medium bg-black/50 px-3 py-1 rounded-full">
                      View in Street View
                    </span>
                  </div>
                </button>

                {/* Travel to next */}
                {stop.travelToNext && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
                    <Navigation className="h-3 w-3" />
                    {stop.travelToNext.duration} · {stop.travelToNext.mode}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {/* Day total */}
          <div className="flex justify-end">
            <p className="text-sm text-muted-foreground">
              Day {i + 1} total: <span className="font-mono font-medium text-foreground">{day.totalCost}</span>
            </p>
          </div>
        </TabsContent>
      ))}
    </Tabs>
  </div>

  {/* RIGHT: Sticky map */}
  <div className="hidden lg:block">
    <div className="sticky top-20 space-y-3">
      <MapView
        itinerary={itinerary}
        activeDay={Number(activeDay)}
        onStopClick={stop => scrollToStop(stop)}
        className="rounded-xl overflow-hidden h-[500px] border"
      />
      <ExportPanel itinerary={itinerary} />
    </div>
  </div>

</div>
```

---

### 6. AccessibilityBadge

```tsx
// Consistent, text + icon, never icon-only
const variants = {
  wheelchair: { icon: '♿', label: 'Accessible',  className: 'bg-green-50 text-green-700 border-green-200' },
  dietary:    { icon: '🌿', label: 'Veg options', className: 'bg-green-50 text-green-700 border-green-200' },
  stepFree:   { icon: '🚶', label: 'Step-free',   className: 'bg-blue-50 text-blue-700 border-blue-200' },
  sensory:    { icon: '🔇', label: 'Quiet',        className: 'bg-purple-50 text-purple-700 border-purple-200' },
}

export function AccessibilityBadge({ type }: { type: keyof typeof variants }) {
  const v = variants[type]
  return (
    <span className={cn("inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full border font-medium", v.className)}>
      <span aria-hidden="true">{v.icon}</span>
      {v.label}
    </span>
  )
}
```

---

### 7. ExportPanel

```tsx
<Card>
  <CardHeader className="pb-3">
    <CardTitle className="text-sm">Export & share</CardTitle>
  </CardHeader>
  <CardContent className="space-y-2">
    <Button className="w-full justify-start gap-2 bg-blue-600 hover:bg-blue-700"
      onClick={exportToCalendar}>
      <CalendarDays className="h-4 w-4" />
      Add to Google Calendar
    </Button>
    <Button variant="outline" className="w-full justify-start gap-2"
      onClick={copyLink}>
      <Link2 className="h-4 w-4" />
      Copy shareable link
    </Button>
    <Separator />
    <Button variant="ghost" size="sm" className="w-full justify-start gap-2 text-muted-foreground"
      onClick={openDisruptionDialog}>
      <RefreshCw className="h-3.5 w-3.5" />
      Trip changed? Re-plan affected days
    </Button>
  </CardContent>
</Card>
```

---

## Google Maps Integration

```tsx
// Dark-adjacent clean style — matches the white UI
const MAP_STYLE = [
  { featureType: "poi", stylers: [{ visibility: "off" }] },
  { featureType: "transit", stylers: [{ visibility: "simplified" }] },
  { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
]

// Custom markers — minimal, brand-colored
const activeMarkerSVG = `
  <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
    <circle cx="16" cy="16" r="12" fill="#2563EB" stroke="white" stroke-width="3"/>
    <text x="16" y="21" text-anchor="middle" fill="white" font-size="11" font-weight="600"
          font-family="Inter, sans-serif">{N}</text>
  </svg>
`
// Route polyline: blue (#2563EB), weight 3, rounded joints
```

---

## Animations (Tailwind only — no extra libraries)

```css
/* globals.css */
@keyframes fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-up {
  animation: fade-up 0.3s ease-out forwards;
}

/* Staggered day cards */
.day-card:nth-child(1) { animation-delay: 0ms; }
.day-card:nth-child(2) { animation-delay: 60ms; }
.day-card:nth-child(3) { animation-delay: 120ms; }
/* etc */
```

```css
/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Responsive Design

```
Mobile (< 768px):
  - Header: logo + current step only (stepper hidden)
  - VibeBoard: single column photo grid
  - ConstraintForm: full-width cards, stacked
  - ItineraryView: day cards full width, map in Sheet (bottom drawer)
  - ExportPanel: fixed bottom bar

Tablet (768px – 1024px):
  - ConstraintForm: 2-col grid for date pickers
  - ItineraryView: map in collapsible panel

Desktop (> 1024px):
  - Full two-column itinerary layout
  - Sticky map sidebar
```

---

## .gitignore (complete — critical before first commit)

```gitignore
# Environment
.env
.env.local
.env.*.local

# Python
.venv/
venv/
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/

# Node / Next.js
node_modules/
.next/
out/
frontend/.next/
frontend/out/
frontend/node_modules/
*.tsbuildinfo

# IDE
.vscode/
.idea/
*.swp
.DS_Store
Thumbs.db

# GCP — NEVER commit service account keys
*-service-account.json
*credentials*.json
gcloud/

# Cloud Build
.cloudbuild/
```

---

## shadcn Component Usage Map

| Screen | Components Used |
|--------|----------------|
| Header | — (custom) |
| VibeBoard | Badge, Button, Skeleton (loading thumbs) |
| ConstraintForm | Card, CardHeader, CardContent, Label, Input, Select, Combobox, Calendar, Popover, Slider, ToggleGroup, Checkbox, Button |
| Loading | Progress, Card |
| ItineraryView | Tabs, TabsList, TabsTrigger, TabsContent, Card, Alert, Badge, Button, Separator |
| MapView | — (custom Google Maps wrapper) |
| ExportPanel | Card, Button, Separator |
| StreetViewModal | Dialog, DialogContent |
| AccessibilityBadge | — (custom using Tailwind) |

---

## Pre-Submission Checklist

```
Design quality:
[ ] All text meets WCAG AA contrast ratio
[ ] No orphaned components (every screen uses shadcn primitives)
[ ] Font loading: next/font with display=swap
[ ] Images: all use next/image with alt props
[ ] Focus rings visible on all interactive elements (Tailwind focus-visible:ring-2)
[ ] Skeleton loading states on all async content
[ ] Empty states handled (no data = meaningful message, not blank)
[ ] Error states handled (shadcn Alert destructive variant)
[ ] Mobile: tested at 375px width
[ ] Reduced motion: animation.css @media rule in place
```