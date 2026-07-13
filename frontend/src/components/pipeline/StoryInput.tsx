'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import type { PipelineInput } from '@/lib/types';

interface StoryInputProps {
  onStart: (input: PipelineInput) => void;
  isLoading: boolean;
}

export default function StoryInput({ onStart, isLoading }: StoryInputProps) {
  const [topic, setTopic] = useState('');
  const [tone, setTone] = useState('');
  const [length, setLength] = useState<PipelineInput['length']>('medium');
  const [platform, setPlatform] =
    useState<PipelineInput['platform']>('cinematic');
  const [enableResearch, setEnableResearch] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    onStart({
      topic: topic.trim(),
      tone: tone.trim() || undefined,
      length,
      platform,
      enableResearch,
    });
  };

  const canSubmit = topic.trim().length > 0 && !isLoading;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl">Create New Story</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Story Topic <span className="text-red-500">*</span>
            </label>
            <Input
              placeholder="e.g., A lone astronaut discovers an ancient alien civilization on Mars"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="grid grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Tone
              </label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                disabled={isLoading}
              >
                <option value="">Auto (wonder)</option>
                <option value="joyful">Joyful</option>
                <option value="sad">Sad</option>
                <option value="tense">Tense</option>
                <option value="wonder">Wonder</option>
                <option value="fear">Fear</option>
                <option value="anger">Anger</option>
                <option value="calm">Calm</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Length
              </label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={length}
                onChange={(e) =>
                  setLength(e.target.value as PipelineInput['length'])
                }
                disabled={isLoading}
              >
                <option value="short">Short (30s)</option>
                <option value="medium">Medium (60s)</option>
                <option value="long">Long (90s)</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Platform
              </label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={platform}
                onChange={(e) =>
                  setPlatform(e.target.value as PipelineInput['platform'])
                }
                disabled={isLoading}
              >
                <option value="cinematic">Cinematic</option>
                <option value="youtube">YouTube</option>
                <option value="tiktok">TikTok</option>
                <option value="instagram">Instagram</option>
              </select>
            </div>

            <div className="space-y-2 pt-6">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableResearch}
                  onChange={(e) => setEnableResearch(e.target.checked)}
                  disabled={isLoading}
                  className="rounded border-input"
                />
                Internet Research
              </label>
            </div>
          </div>

          <Button
            type="submit"
            disabled={!canSubmit}
            className="w-full"
          >
            {isLoading ? 'Starting Pipeline…' : 'Generate Story'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}