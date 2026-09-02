'use client';

const testimonials = [
  {
    quote: 'I wrote my first screenplay prompt at midnight. By morning I had a full scene breakdown with camera directions I could hand to any DP.',
    author: 'Amina K.',
    role: 'Indie Filmmaker',
    accent: 'from-red-400 to-orange-400',
  },
  {
    quote: 'The cinematic prompts are incredibly specific — lens type, color temperature, aperture. It reads like a real camera report.',
    author: 'Derek L.',
    role: 'VP of Production, StudioX',
    accent: 'from-blue-400 to-purple-400',
  },
  {
    quote: 'Finally, a tool that understands the difference between a wide shot and an extreme close-up. That alone is worth it.',
    author: 'Priya M.',
    role: 'Director of Photography',
    accent: 'from-green-400 to-teal-400',
  },
];

export default function TestimonialsSection() {
  return (
    <section className="relative py-32 bg-gradient-to-b from-black via-slate-950/60 to-black overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      <div className="max-w-[1200px] mx-auto px-6 md:px-8">
        <div className="text-center mb-20">
          <span className="pill-badge-dark mb-6 inline-block">What Creators Say</span>
          <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
            Built for people who
            <br />
            <span className="gradient-text">make things.</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div key={i} className={`feature-card-dark rounded-xl p-8 flex flex-col relative overflow-hidden group cursor-default hover:border-white/10 transition-all duration-500`}>
              {/* Accent corner */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${t.accent} opacity-40 group-hover:opacity-80 transition-opacity`} />
              
              {/* Quote mark */}
              <span className="text-5xl text-white/[0.06] font-serif leading-none mb-4">&ldquo;</span>
              
              <p className="text-white/60 text-sm leading-relaxed flex-grow mb-8">
                {t.quote}
              </p>

              <div className="flex items-center gap-3 pt-5 border-t border-white/[0.06]">
                <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${t.accent} flex items-center justify-center text-black font-bold text-sm`}>
                  {t.author[0]}
                </div>
                <div>
                  <p className="text-sm font-bold text-white/90">{t.author}</p>
                  <p className="text-xs text-white/35">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
