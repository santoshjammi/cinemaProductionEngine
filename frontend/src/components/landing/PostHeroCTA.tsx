'use client';

export default function PostHeroCTA() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-black via-red-950/15 to-black overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full bg-red-500/6 blur-[140px]" />

      <div className="relative z-10 max-w-[800px] mx-auto px-6 md:px-8 text-center">
        <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
          Your next film starts with
          <br />
          <span className="gradient-text">a single sentence.</span>
        </h2>
        <p className="text-white/50 text-lg mb-10 leading-relaxed max-w-[600px] mx-auto">
          Open the pipeline. Type your idea. Watch as AI handles the rest — from research to final output. No setup, no dependencies, no limits.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="/create" className="cta-primary text-base">
            Try It Now — Free
          </a>
          <a href="/projects" className="cta-secondary text-base">
            Browse Projects
          </a>
        </div>
      </div>

      {/* Bottom line */}
      <div className="absolute bottom-0 left-0 right-0 h-px gradient-accent-line" />
    </section>
  );
}
