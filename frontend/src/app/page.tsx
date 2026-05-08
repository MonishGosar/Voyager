/**
 * Home page — renders the Voyager landing hero.
 *
 * This is the root route ("/") that presents the value proposition
 * and primary CTA to start the travel planning wizard.
 */

import LandingHero from "@/components/landing/LandingHero";

/**
 * Home page component.
 *
 * @returns The landing page with the LandingHero section.
 */
export default function Home(): JSX.Element {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <LandingHero />
    </main>
  );
}
