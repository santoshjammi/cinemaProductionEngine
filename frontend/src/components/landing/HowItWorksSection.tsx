'use client';

const stages = [
  { order: 0, label: 'RESEARCH', icon: '🔍' },
  { order: 1, label: 'STORY', icon: '✍️' },
  { order: 2, label: 'SCENES', icon: '🎬' },
  { order: 3, label: 'DIALOGUE', icon: '💬' },
  { order: 4, label: 'PROMPTS', icon: '📋' },
  { order: 5, label: 'VALIDATE', icon: '✅' },
];

export default function HowItWorksSection() {
  let connectingLineIndex = -1;

  return (
    <section id="how-it-works" className="relative py-32 bg-gradient-to-b from-black via-slate-950 to-black overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      <div className="max-w-[1000px] mx-auto px-6 md:px-8">
        <div className="text-center mb-24">
          <span className="pill-badge-dark mb-6 inline-block">How It Works</span>
          <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
            Six stages.
            <br />
            <span className="gradient-text-light">One click.</span>
          </h2>
          <p className="text-white/50 max-w-[500px] mx-auto text-lg">
            Describe your idea in one sentence. Your AI pipeline does the rest.
          </p>
        </div>

        {/* Pipeline visualization */}
        <div className="relative">
          {/* Connection lines - manually positioned between each stage's vertical center */}
          {stages.map((stage, index) => {
            const isLast = index === stages.length - 1;
            let topOffset = '';
            if (index >= connectingLineIndex + 1) {
              // Calculate the midpoint between current and previous stage
              const prevY = index > 0 ? (stages[index - 1].order + 0.5) * 80 : (stage.order + 0.5) * 40;
              topOffset = `top-[${prevY}px]`;
              connectingLineIndex = index;
            }

            return (
              <div key={stage.label} className="relative flex items-center gap-6 md:gap-10 mb-8">
                {/* Left: stage indicator */}
                <div className="flex-shrink-0 w-20 md:w-24 h-20 md:h-24 rounded-2xl bg-gradient-to-br from-slate-900 to-black border border-white/10 flex items-center justify-center text-3xl md:text-4xl relative overflow-hidden">
                  {stage.icon}
                  <div className={`absolute inset-0 bg-gradient-to-br ${index < 3 ? 'from-red-500/20 to-transparent' : index < 5 ? 'from-amber-500/15 to-transparent' : 'from-green-500/15 to-transparent'} opacity-0 hover:opacity-100 transition-opacity duration-500`} />
                </div>

                {/* Connection line */}
                {!isLast && (
                  <div className="absolute left-[calc(5rem+1rem)] md:left-[calc(6rem+2.5rem)] w-[2px] h-8 -mb-8 bg-gradient-to-b from-white/20 to-transparent" />
                )}

                {/* Right: content */}
                <div className="flex-grow">
                  <p className="text-[10px] tracking-[0.3em] text-red-400 font-mono mb-1">
                    STAGE {stage.order + 1}/6 &mdash; {stage.label}
                  </p>
                  <h3 className="text-xl md:text-2xl font-bold text-white mb-2 tracking-tight">
                    {stages[index] === stages[0] ? 'AI gathers world knowledge' : 
                     stages[index] === stages[1] ? 'Your story comes alive' :
                     stages[index] === stages[2] ? 'Shot-by-shot decomposition' :
                     stages[index] === stages[3] ? 'Dialogue that sounds human' :
                     stages[index] === stages[4] ? 'Production-ready cinematic prompts' :
                     'Quality ensured at every step'}
                  </h3>
                  <p className="text-white/40 text-sm">
                    {stages[index] === stages[0] ? 'Search across billions of published works to build your story\'s foundation.' :
                     stages[index] === stages[1] ? 'Character arcs, plot structure, emotional beats — all generated autonomously.' :
                     stages[index] === stages[2] ? 'Every scene mapped with camera angles, lighting, and composition specs.' :
                     stages[index] === stages[3] ? 'Lines written by characters with genuine voice and intention.' :
                     stages[index] === stages[4] ? 'Camera type, lens, aperture, motion — every cinematic parameter defined.' :
                     'Multi-dimensional scoring: coherence, continuity, emotion, spectacle.'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-20">
          <a href="/create" className="cta-primary text-base inline-flex items-center gap-3">
            Watch How It Flows
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14" /><path d="M12 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>
    </section>
  );
}
