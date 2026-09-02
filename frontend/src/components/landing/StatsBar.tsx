'use client';

const stats = [
  { value: '100%', label: 'AI-Native', description: 'No human creative steps needed' },
  { value: '6', label: 'Pipeline Stages', description: 'Research to final output' },
  { value: 'Zero', label: 'API Keys Required', description: 'Runs completely local' },
  { value: 'Free', label: 'Lifetime Tier', description: 'No credit card, no trials' },
];

export default function StatsBar() {
  return (
    <section className="relative py-20 bg-gradient-to-b from-black via-red-950/[0.04] to-black overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />
      
      <div className="max-w-[1200px] mx-auto px-6 md:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 md:gap-12">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-[clamp(2rem,4vw,3.5rem)] font-mono font-bold text-white mb-2 gradient-text">
                {stat.value}
              </p>
              <p className="text-sm font-bold text-white/80 mb-1 tracking-tight">{stat.label}</p>
              <p className="text-xs text-white/30">{stat.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
