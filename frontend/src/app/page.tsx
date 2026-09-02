'use client';

import { useEffect, useRef } from 'react';
import HeroSection from '@/components/landing/HeroSection';
import PostHeroCTA from '@/components/landing/PostHeroCTA';
import TrustBadgeStrip from '@/components/landing/TrustBadgeStrip';
import StatsBar from '@/components/landing/StatsBar';
import FeaturesSection from '@/components/landing/FeaturesSection';
import TestimonialsSection from '@/components/landing/TestimonialsSection';
import ShowcaseSection from '@/components/landing/ShowcaseSection';
import HowItWorksSection from '@/components/landing/HowItWorksSection';
import FAQSection from '@/components/landing/FAQSection';
import FinalCTASection from '@/components/landing/FinalCTASection';
import { AdManager } from '@/components/ads/AdManager';

export default function Home() {
  const adRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      AdManager.instance().activateAll();
      return () => AdManager.instance().deactivateAll();
    } catch {/* fail closed */}
  }, []);

  return (
    <main>
      {/* Header banner ad slot */}
      <div data-ad-slot="ad_banner_header" className="banner-ad-container min-h-[90px] flex items-center justify-center bg-black/5">
        <span className="text-xs text-zinc-600">Advertisement</span>
      </div>

      <HeroSection />

      {/* Post-hero conversion */}
      <PostHeroCTA />

      {/* Trust strip — powered-by infrastructure logos */}
      <TrustBadgeStrip />

      {/* Social proof stats */}
      <StatsBar />

      {/* Mid-content divider with sidebar placeholder */}
      <div className="relative py-32 bg-gradient-to-b from-black via-red-950/10 to-black overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

        {/* Sidebar ad slot on wide views */}
        <aside className="hidden lg:block fixed right-0 top-[120px] w-[300px] h-[250px] z-40 pointer-events-none">
          <div data-ad-slot="ad_banner_sidebar" className="w-full h-full flex items-center justify-center bg-black/5 border-l border-zinc-800/20">
            <span className="text-xs text-zinc-600">Ad</span>
          </div>
        </aside>

        {/* FeaturesSection moved here for ad integration */}
        <div className="max-w-[900px] mx-auto lg:mr-[340px] px-6 md:px-8">
          <FeaturesSection />
        </div>
      </div>

      {/* Trust testimonials */}
      <TestimonialsSection />

      <ShowcaseSection />
      
      {/* FAQ — objection handling before final CTA */}
      <FAQSection />

      <HowItWorksSection />

      {/* Final CTA — last marketing push before footer */}
      <FinalCTASection />

      {/* Pre-footer banner ad slot */}
      <div data-ad-slot="ad_banner_prefooter" className="banner-ad-container max-w-[900px] mx-auto px-6 md:px-8 mb-12 min-h-[90px] flex items-center justify-center bg-black/5">
        <span className="text-xs text-zinc-600">Advertisement</span>
      </div>
    </main>
  );
}
