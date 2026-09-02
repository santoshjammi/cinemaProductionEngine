'use client';

export default function FinalCTASection() {
  return (
    <section className="relative py-32 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-red-950/10 to-black" />
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      {/* Ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] rounded-full bg-red-500/8 blur-[120px]" />

      {/* Grid overlay */}
      <div className="absolute inset-0 opacity-[0.015]" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)' }} />

      <div className="relative z-10 text-center max-w-[800px] mx-auto px-6 md:px-8">
        {/* Headline */}
        <h2 className="text-[clamp(2.25rem,6vw,4.5rem)] font-mono font-bold tracking-tighter leading-[0.95] text-white mb-6">
          Your story is ready.
          <br />
          <span className="gradient-text">Go make it real.</span>
        </h2>

        {/* Description */}
        <p className="text-base md:text-lg text-white/50 max-w-[600px] mx-auto mb-10 leading-relaxed">
          Join creators who are already using videoGen to produce cinematic content in minutes — not months. From first draft to final cut, the entire pipeline runs on autopilot.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="/create" className="cta-primary text-lg px-10 py-4">
            Get Started Free
          </a>
          <a href="#how-it-works" className="cta-secondary text-lg flex items-center gap-2 px-8 py-4">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
            See How It Works
          </a>
        </div>

        {/* Risk reversal */}
        <div className="flex items-center justify-center gap-6 text-xs text-white/25 mt-8">
          <span className="flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
            Free tier included
          </span>
          <span className="w-1 h-1 rounded-full bg-white/20" />
          <span className="flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
            No credit card
          </span>
          <span className="w-1 h-1 rounded-full bg-white/20" />
          <span className="flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
            Cancel anytime
          </span>
        </div>
      </div>

      {/* Bottom line */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </section>
  );
}
