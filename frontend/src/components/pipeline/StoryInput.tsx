'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Button } from '@/components/ui/Button';
import type { PipelineInput, ProductionProfile } from '@/lib/types';
import { listProductionProfiles } from '@/lib/api';

interface StoryInputProps {
  onStart: (input: PipelineInput) => void;
  isLoading: boolean;
  onSynopsisChange?: (synopsis: string) => void;
}

const visualStyles = [
  "Cinematic Realism", "Anime/Manga", "Documentary", "Abstract/Conceptual", 
  "3D Render", "Noir/Shadow", "Vintage/Film Grain"
];
const audioMoods = ["Ominous", "Uplifting", "Tense", "Melancholic", "Epic", "Calm"];

function parseSynopsis(text: string): Record<string, string> {
  const fields: Record<string, string> = {};
  const lines = text.split('\n');
  let currentKey = '';
  let currentValue: string[] = [];

  const sectionHeaders: Record<string, string> = {
    'title': 'title',
    'core_fear': 'core_fear',
    'synopsis': 'synopsis',
    'key_characters': 'key_characters',
    'emotional_arc': 'emotional_arc',
    'ending': 'ending',
  };

  const flush = () => {
    if (currentKey && currentValue.length > 0) {
      fields[currentKey] = currentValue.join('\n').trim();
    }
    currentValue = [];
  };

  for (const line of lines) {
    const trimmed = line.trim().toLowerCase();
    // STORY 01 — Title
    const storyMatch = line.match(/^STORY\s+\S+\s*[—\-]\s*(.+)$/i);
    if (storyMatch) {
      flush();
      fields['title'] = storyMatch[1].trim();
      currentKey = '';
      continue;
    }
    if (sectionHeaders[trimmed]) {
      flush();
      currentKey = sectionHeaders[trimmed];
      continue;
    }
    if (currentKey) {
      currentValue.push(line);
    }
  }
  flush();
  return fields;
}

export default function StoryInput({ onStart, isLoading, onSynopsisChange }: StoryInputProps) {
  const [rawSynopsis, setRawSynopsis] = useState('');
  const [title, setTitle] = useState('');
  const [coreFear, setCoreFear] = useState('');
  const [synopsisBody, setSynopsisBody] = useState('');
  const [keyCharacters, setKeyCharacters] = useState('');
  const [emotionalArc, setEmotionalArc] = useState('');
  const [ending, setEnding] = useState('');
  const [tone, setTone] = useState('');
  const [length, setLength] = useState<PipelineInput['length']>('conversational');
  const [platform, setPlatform] = useState<PipelineInput['platform']>('cinematic');
  const [enableResearch, setEnableResearch] = useState(true);
  const [targetAudience, setTargetAudience] = useState('');
  const [callToAction, setCallToAction] = useState('');
  const [visualStyle, setVisualStyle] = useState(visualStyles[0]);
  const [musicMood, setMusicMood] = useState(audioMoods[0]);
  const [profiles, setProfiles] = useState<ProductionProfile[]>([]);
  const [profileId, setProfileId] = useState<string>('');

  useEffect(() => {
    let mounted = true;
    listProductionProfiles()
      .then((res) => {
        if (!mounted) return;
        setProfiles(res.profiles || []);
        const def = (res.profiles || []).find((p) => p.default);
        setProfileId(def?.id || res.profiles[0]?.id || '');
      })
      .catch(() => { /* silent — UI still works without profiles */ });
    return () => { mounted = false; };
  }, []);

  const handleParse = useCallback(() => {
    const parsed = parseSynopsis(rawSynopsis);
    if (parsed.title) setTitle(parsed.title);
    if (parsed.core_fear) setCoreFear(parsed.core_fear);
    if (parsed.synopsis) setSynopsisBody(parsed.synopsis);
    if (parsed.key_characters) setKeyCharacters(parsed.key_characters);
    if (parsed.emotional_arc) setEmotionalArc(parsed.emotional_arc);
    if (parsed.ending) setEnding(parsed.ending);
  }, [rawSynopsis]);

  // Build full synopsis for Genesis
  useEffect(() => {
    if (onSynopsisChange) {
      const parts: string[] = [];
      if (title) parts.push(`TITLE: ${title}`);
      if (coreFear) parts.push(`CORE FEAR: ${coreFear}`);
      if (keyCharacters) parts.push(`CHARACTERS: ${keyCharacters}`);
      if (emotionalArc) parts.push(`EMOTIONAL ARC: ${emotionalArc}`);
      if (ending) parts.push(`ENDING: ${ending}`);
      if (synopsisBody) parts.push('', synopsisBody);
      onSynopsisChange(parts.join('\n') || rawSynopsis);
    }
  }, [title, coreFear, synopsisBody, keyCharacters, emotionalArc, ending, rawSynopsis, onSynopsisChange]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!synopsisBody.trim() && !rawSynopsis.trim()) return;

    onStart({
      topic: title || synopsisBody.slice(0, 80) || rawSynopsis.slice(0, 80),
      tone: tone.trim() || undefined,
      length,
      platform,
      enableResearch,
      profileId: profileId || undefined,
      producerBrief: {
        title: title || 'Untitled',
        logline: title || synopsisBody.slice(0, 80) || rawSynopsis.slice(0, 80),
        targetAudience: targetAudience || "General",
        callToAction: callToAction || "",
        totalDuration: length === 'conversational' ? '900-1200s' : length === 'short' ? '60s' : length === 'medium' ? '120s' : '300s+',
        aspectRatio: platform === 'tiktok' ? '9:16' : platform === 'youtube' ? '16:9' : '16:9',
        pacingStyle: length === 'conversational' ? 'relaxed' : tone.toLowerCase() === 'tense' || tone.toLowerCase() === 'fast' ? 'fast' : 'medium',
        visualStyleGuide: [visualStyle],
        musicMood: musicMood,
        voiceOverStyle: tone || "Narrative",
        multiProductGoals: ["video"], 
      }
    });
  };

  const canSubmit = (synopsisBody.trim().length > 0 || rawSynopsis.trim().length > 0) && !isLoading;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Project Configuration (Genesis)</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Raw synopsis input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Synopsis <span className="text-muted-foreground font-normal">(paste structured format, then click Parse)</span>
            </label>
            <Textarea
              placeholder={`STORY 01 — The Hand He Never Reached For\n\nTITLE\nThe Hand He Never Reached For\n\nCORE_FEAR\nFear of Rejection\n\nSYNOPSIS\nYour story here...\n\nKEY_CHARACTERS\nArjun (34) – Husband\n\nEMOTIONAL_ARC\nWarmth → Withdrawal → Understanding\n\nENDING\nThe audience realizes...`}
              value={rawSynopsis}
              onChange={(e) => setRawSynopsis(e.target.value)}
              className="min-h-[200px] text-sm font-mono"
            />
            <Button type="button" variant="outline" size="sm" onClick={handleParse} className="mt-1">
              Parse & Fill Fields
            </Button>
          </div>

          <div className="border-t pt-4 space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Parsed Fields</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Title</label>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Story title" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Core Fear</label>
                <Input value={coreFear} onChange={(e) => setCoreFear(e.target.value)} placeholder="e.g. Fear of Rejection" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Synopsis</label>
              <Textarea value={synopsisBody} onChange={(e) => setSynopsisBody(e.target.value)} className="min-h-[120px] text-sm" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Key Characters</label>
                <Textarea value={keyCharacters} onChange={(e) => setKeyCharacters(e.target.value)} className="min-h-[80px] text-sm" placeholder="Arjun (34) – Husband" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Emotional Arc</label>
                <Input value={emotionalArc} onChange={(e) => setEmotionalArc(e.target.value)} placeholder="Warmth → Withdrawal → Understanding" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Ending</label>
              <Textarea value={ending} onChange={(e) => setEnding(e.target.value)} className="min-h-[60px] text-sm" />
            </div>
          </div>

          {/* Director's Brief Section */}
          <div className="p-4 bg-muted/50 rounded-lg space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Director's Brief</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs">Target Audience</label>
                <select 
                  value={targetAudience} 
                  onChange={(e) => setTargetAudience(e.target.value)}
                  className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
                >
                  <option value="">General</option>
                  <option value="Educators">Educators</option>
                  <option value="Gamers">Gamers</option>
                  <option value="Business Leaders">Business Leaders</option>
                  <option value="Developers">Developers</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs">Visual Style Guide</label>
                <select 
                  value={visualStyle} 
                  onChange={(e) => setVisualStyle(e.target.value)}
                  className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
                >
                  {visualStyles.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs">Audio Mood</label>
                <select 
                  value={musicMood} 
                  onChange={(e) => setMusicMood(e.target.value)}
                  className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
                >
                  {audioMoods.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs">Platform/Format</label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value as PipelineInput['platform'])}
                  className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
                >
                  <option value="cinematic">Cinematic</option>
                  <option value="youtube">YouTube (Horizontal)</option>
                  <option value="tiktok">TikTok (Vertical)</option>
                  <option value="instagram">Instagram/Reels</option>
                </select>
              </div>
              <div className="space-y-2 col-span-2">
                <label className="text-xs">Production Profile (runtime target)</label>
                <select
                  value={profileId}
                  onChange={(e) => setProfileId(e.target.value)}
                  className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
                  disabled={profiles.length === 0}
                >
                  {profiles.length === 0 && <option value="">Default (15-20 min)</option>}
                  {profiles.map((p) => {
                    const runtime = p.runtime;
                    return (
                      <option key={p.id} value={p.id}>
                        {p.label} — {runtime?.minimum_minutes}-{runtime?.maximum_minutes} min
                        {p.default ? ' (default)' : ''}
                      </option>
                    );
                  })}
                </select>
                <p className="text-[10px] text-muted-foreground">
                  Controls target runtime, scene count, and per-scene duration. GENESIS uses this to plan the story structure.
                </p>
              </div>
            </div>
          </div>

          {/* Legacy/Quick Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Length</label>
              <select 
                value={length} 
                onChange={(e) => setLength(e.target.value as PipelineInput['length'])}
                className="w-full h-10 px-3 py-2 text-sm border rounded-md bg-background"
              >
                <option value="conversational">Conversational (15-20 min)</option>
                <option value="short">Short (approx 60s)</option>
                <option value="medium">Medium (approx 2-3 min)</option>
                <option value="long">Long-Form (Course/Doc)</option>
              </select>
            </div>
            <div className="flex items-end pb-1">
               <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={enableResearch} onChange={(e) => setEnableResearch(e.target.checked)} disabled={isLoading} />
                  Include Research Context
               </label>
            </div>
          </div>

          <Button type="submit" disabled={!canSubmit} className="w-full">
            {isLoading ? 'Initializing Genesis...' : 'Start Story Generation'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
