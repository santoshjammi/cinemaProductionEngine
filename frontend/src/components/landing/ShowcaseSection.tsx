'use client';

export default function ShowcaseSection() {
  const shots = [
    { aspect: 'Wide landscape', style: 'Cinematic drone shot. The hero walks across a sunlit mesa overlooking ancient ruins.' },
    { aspect: 'Tight close-up', style: 'Extreme close-up. Eyes reflecting the burning of a village in the distance.' },
    { aspect: 'Dynamic tracking', style: 'Steadicam follows two characters running through narrow alleyways with expressive dialogue.' },
    { aspect: 'Silent beauty', style: 'Wide establishing shot. Silent tension before the storm. Desaturated color grade.' },
  ];

  return (
    <section className="relative py-32 bg-gradient-to-b from-black via-red-950/10 to-black overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      <div className="max-w-[1200px] mx-auto px-6 md:px-8">
        <div className="text-center mb-16">
          <span className="pill-badge-dark mb-6 inline-block">Shot Quality</span>
          <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
            Every shot. Directed by AI.
            <br />
            <span className="gradient-text-light">Shot by shot.</span>
          </h2>
        </div>

        {/* Shot cards - not video grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {shots.map((shot, i) => (
            <div key={i} className="feature-card-dark rounded-xl overflow-hidden group cursor-default hover:border-white/10 transition-all duration-500">
              {/* Visual placeholder */}
              <div className="aspect-[21/9] bg-gradient-to-br from-slate-900 to-black relative overflow-hidden flex items-center justify-center">
                <div className={`absolute inset-0 opacity-20 ${i === 0 ? 'bg-gradient-to-br from-orange-600/30 to-transparent' : 
                  i === 1 ? 'bg-gradient-to-br from-red-700/30 to-transparent' :
                  i === 2 ? 'bg-gradient-to-br from-blue-700/30 to-transparent' :
                  'bg-gradient-to-br from-slate-700/30 to-transparent'}`} />
                <span className="text-6xl opacity-40 z-10 relative">
                  {['🌄', '👁️', '🏃', '🌑'][i]}
                </span>
              </div>
              
              {/* Info */}
              <div className="p-6">
                <p className="text-[10px] tracking-[0.3em] text-red-400 font-mono mb-2">{shot.aspect.toUpperCase()}</p>
                <p className="text-white/50 text-sm leading-relaxed">{`"${shot.style}"`}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Keyframe examples below */}
        <div className="mt-12 feature-card-dark rounded-xl p-8 md:p-12 flex flex-col md:flex-row gap-8 items-start md:items-center">
          <div className="flex-shrink-0 w-48 h-27 bg-black/60 rounded-lg relative overflow-hidden border border-white/5 flex items-center justify-center">
            <span className="text-3xl opacity-50">🎞️</span>
          </div>
          <div>
            <p className="text-[10px] tracking-[0.3em] text-amber-400 font-mono mb-2">CINEMATIC PROMPT ENGINE</p>
            <p className="text-white/70 text-sm md:text-base leading-relaxed mb-4 font-light">
              Every AI-generated shot comes with its own cinematic prompt — the exact camera instructions that an AI video model needs:
            </p>
            <div className="bg-black/60 rounded-lg p-5 border border-white/5 max-w-xl">
              <code className="text-xs text-amber-200 font-mono block leading-relaxed">
                wide_angle, drone_aerial_shot, golden_hour_lighting, slow_push_in, 
                temperature=3200k, aspect_ratio=21:9, depth_of_field=f/2.8, 
                motion_blur=180deg_shutter, color_grade=teal_orange
              </code>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
