'use client';

import { useState } from 'react';

const faqs = [
  {
    q: 'What exactly does videoGen do?',
    a: 'videoGen is an AI-native filmmaking platform. You type your story idea — one sentence is enough — and the pipeline researches, writes a script, breaks it into scenes, generates dialogue, creates cinematic camera prompts, and validates everything automatically.',
  },
  {
    q: 'Do I need any filmmaking experience?',
    a: 'No. If you can write a sentence, you can use videoGen. The platform handles all the creative and technical complexity — camera angles, lighting ratios, scene composition, character development — so you focus on your vision.',
  },
  {
    q: 'Is this free to use?',
    a: 'Yes, there is a lifetime free tier with no credit card required. We believe everyone should be able to start creating without financial barriers.',
  },
  {
    q: 'What AI models does videoGen use?',
    a: 'videoGen runs entirely local-first using Ollama with Qwen3.6 for reasoning and planning. It also integrates FLUX for image generation, EdgeTTS for voice synthesis, and FFmpeg for video assembly.',
  },
  {
    q: 'Can I export the output for professional production?',
    a: 'Absolutely. Every scene comes with detailed camera reports — lens specifications, composition notes, lighting ratios, motion descriptors — that you can hand to any cinematographer or DOP.',
  },
  {
    q: 'How is this different from other AI writing tools?',
    a: 'Other tools stop at text generation. videoGen goes the full distance: research -> story -> scenes -> dialogue -> cinematic prompts -> validation. Every stage is automated and interconnected, producing production-ready outputs not just rough drafts.',
  },
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section className="relative py-32 bg-gradient-to-b from-black via-slate-950/40 to-black overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-px gradient-accent-line" />

      <div className="max-w-[800px] mx-auto px-6 md:px-8">
        <div className="text-center mb-16">
          <span className="pill-badge-dark mb-6 inline-block">FAQ</span>
          <h2 className="text-[clamp(2rem,5vw,3.5rem)] font-mono font-bold tracking-tighter text-white mb-6">
            Questions? Answered.
          </h2>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <div key={i} className="feature-card-dark rounded-xl overflow-visible cursor-default hover:border-white/10 transition-all duration-300">
              <button
                type="button"
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full px-7 py-5 flex items-center justify-between text-left"
              >
                <span className="text-sm font-semibold text-white/90 pr-4">{faq.q}</span>
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className={`flex-shrink-0 text-white/30 transition-transform duration-200 ${openIndex === i ? 'rotate-180' : ''}`}
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </button>
              {openIndex === i && (
                <div className="px-7 pb-5">
                  <p className="text-sm text-white/45 leading-relaxed">{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Bottom line */}
      <div className="absolute bottom-0 left-0 right-0 h-px gradient-accent-line" />
    </section>
  );
}
