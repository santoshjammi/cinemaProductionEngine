'use client';

export default function HeroSection() {
  return (
    <section className="relative min-h-[100vh] flex items-center justify-center hero-gradient overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-red-500/8 glow-amber blur-[120px]" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full bg-amber-500/5 blur-[100px]" />

      {/* Grid overlay */}
      <div className="absolute inset-0 opacity-[0.02]" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)' }} />

      <div className="relative z-10 text-center max-w-[1100px] mx-auto px-6 md:px-8">
        {/* Badge */}
        <div
          className="inline-flex items-center gap-2 pill-badge-dark mb-8 animate-fade-in-up"
        >
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Now in Public Beta â€” Free for Creators
        </div>

        {/* Main headline */}
        <h1 className="text-[clamp(3rem,8vw,7rem)] font-mono font-bold tracking-tighter leading-[0.95] text-cine-shadow mb-6 animate-fade-in-up animate-delay-200">
          From script to
          <br />
          <span className="gradient-text">feature film.</span>
        </h1>

        {/* Subheadline */}
        <p className="text-lg md:text-xl text-white/60 max-w-[750px] mx-auto mb-10 leading-relaxed font-light animate-fade-in-up animate-delay-400">
          videoGen is the first AI-native filmmaking platform that handles everything â€” research, story development, scene generation, dialogue, cinematic prompts, and quality validation â€” in one seamless pipeline.
        </p>

        {/* CTA buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-fade-in-up animate-delay-600">
          <a href="/create" className="cta-primary text-base">
            Start Creating &mdash; It&amp;apos;s Free
          </a>
          <a href="#how-it-works" className="cta-secondary text-base flex items-center gap-2">
            {/* Play icon */}
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
            Watch Demo
          </a>
        </div>

        {/* Social proof micro */}
        <div className="flex items-center justify-center gap-6 text-xs text-white/30 animate-fade-in-up animate-delay-600">
          <span>No credit card required</span>
          <span className="w-1 h-1 rounded-full bg-white/20" />
          <span>Lifetime free tier available</span>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
          <span className="text-white/20 text-xs tracking-widest uppercase">Discover</span>
          <div className="w-px h-6 bg-gradient-to-b from-white/30 to-transparent" />
        </div>
      </div>
    </section>
  );
}
