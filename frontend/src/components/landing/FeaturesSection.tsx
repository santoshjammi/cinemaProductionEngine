'use client';

const features = [
  {
    title: 'Internet Research',
    description: 'AI scans billions of sources to gather world-class context for your story, building a research foundation no human could match.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    ),
    accent: 'from-red-400 to-orange-400',
  },
  {
    title: 'Story Generation',
    description: 'Your story engine transforms raw research into compelling narratives with character arcs, plot structure, and emotional depth.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4Z" />
      </svg>
    ),
    accent: 'from-yellow-400 to-amber-400',
  },
  {
    title: 'Scene Breakdown',
    description: 'Automatically decompose your story into shot-ready scenes with camera directions, lighting notes, and production metadata.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <path d="M8 21h8" />
        <path d="M12 17v4" />
      </svg>
    ),
    accent: 'from-green-400 to-teal-400',
  },
  {
    title: 'Dialogue Writing',
    description: 'Character-aware dialogue that sounds authentic. Each line shaped by personality, context, and the emotional trajectory of your story.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
      </svg>
    ),
    accent: 'from-blue-400 to-purple-400',
  },
  {
    title: 'Cinematic Prompts',
    description: 'Generate production-grade prompts for every shot — camera angles, lens specs, lighting ratios, color grade, and motion descriptors.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M14.5 4h-5L7 7H4a2 2 0 00-2 2v9a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2h-3l-2.5-3z" />
        <circle cx="12" cy="13" r="3" />
      </svg>
    ),
    accent: 'from-pink-400 to-red-400',
  },
  {
    title: 'Validation & Metrics',
    description: 'Every output passes through AI quality gates — narrative coherence, visual continuity, and production readiness scored in real time.',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    ),
    accent: 'from-cyan-400 to-blue-400',
  },
];

export default function FeaturesSection() {
  return (
    <section className="relative py-32 bg-black overflow-hidden">
      {/* Top line */}
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      <div className="max-w-[1200px] mx-auto px-6 md:px-8">
        {/* Section header */}
        <div className="text-center mb-20">
          <span className="pill-badge-dark mb-6 inline-block">Capabilities</span>
          <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
            Six stages. One pipeline.
            <br />
            <span className="gradient-text-light">End to end.</span>
          </h2>
          <p className="text-white/50 max-w-[600px] mx-auto text-lg">
            Every stage of filmmaking, automated by AI and orchestrated in a single workflow.
          </p>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className="feature-card-dark group rounded-xl p-8 cursor-default"
            >
              <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${feature.accent} flex items-center justify-center text-black mb-6 transition-transform duration-500 group-hover:scale-110`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3 tracking-tight">
                {feature.title}
              </h3>
              <p className="text-white/50 leading-relaxed text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
