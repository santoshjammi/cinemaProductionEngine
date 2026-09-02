'use client';

const logos = [
  { name: 'ComfyUI', description: 'Image Rendering' },
  { name: 'FLUX', description: 'Diffusion Engine' },
  { name: 'Edge TTS', description: 'Voice Synthesis' },
  { name: 'FFmpeg', description: 'Video Assembly' },
  { name: 'Ollama', description: 'Local Inference' },
  { name: 'Python', description: 'Pipeline Core' },
];

export default function TrustBadgeStrip() {
  return (
    <section className="relative py-16 bg-gradient-to-r from-black via-zinc-950 to-black overflow-hidden">
      <div className="max-w-[1200px] mx-auto px-6 md:px-8">
        <p className="text-center text-xs tracking-[0.4em] text-white/25 uppercase mb-10 font-mono">
          Powered by modern AI infrastructure
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
          {logos.map((item) => (
            <div
              key={item.name}
              className="flex flex-col items-center gap-2 group cursor-default"
            >
              <div className="w-[70px] h-[40px] rounded-lg bg-white/[0.02] border border-white/[0.06] flex items-center justify-center transition-all duration-300 group-hover:bg-white/[0.05] group-hover:border-white/[0.12]">
                <span className="text-sm font-mono text-white/40 group-hover:text-white/70 transition-colors">
                  {item.name}
                </span>
              </div>
              <span className="text-[9px] tracking-[0.2em] text-white/[0.15] uppercase">{item.description}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
