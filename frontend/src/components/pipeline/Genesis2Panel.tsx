'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Textarea } from '@/components/ui/Textarea';
import type { Genesis2PhaseResult, Genesis2Summary } from '@/lib/types';
import * as api from '@/lib/api';

interface Genesis2PanelProps {
  synopsis: string;
  onComplete: (pkg: any) => void;
}

const PHASE_NAMES = [
  'Creative Understanding',
  'Story Foundation',
  'Character Psychology',
  'World Development',
  'Narrative Expansion',
  'Scene Planning',
  'Dialogue Planning',
  'Visual Language',
  'Production Specifications',
  'Validation',
  'Creative Critique',
  'Knowledge Integration',
];

export default function Genesis2Panel({ synopsis, onComplete }: Genesis2PanelProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentPhase, setCurrentPhase] = useState<number>(0);

  const handleRun = async () => {
    if (!synopsis.trim()) return;
    setIsRunning(true);
    setError(null);
    setCurrentPhase(0);

    // Simulate phase progress while waiting for the backend
    const progressInterval = setInterval(() => {
      setCurrentPhase((p) => Math.min(p + 1, 12));
    }, 30000);

    try {
      const data = await api.runGenesis2(synopsis);
      clearInterval(progressInterval);
      setCurrentPhase(12);
      setResult(data);
      onComplete(data);
    } catch (err: any) {
      clearInterval(progressInterval);
      setError(err.message || 'Genesis2 pipeline failed');
    } finally {
      setIsRunning(false);
    }
  };

  const getPhaseIcon = (phase: Genesis2PhaseResult) => {
    switch (phase.status) {
      case 'completed': return '✅';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  const getPhaseBadge = (phase: Genesis2PhaseResult) => {
    if (phase.validationIssues > 0) return <Badge variant="warning">{phase.validationIssues} issues</Badge>;
    if (phase.critiqueFindings > 0) return <Badge variant="outline">{phase.critiqueFindings} findings</Badge>;
    return null;
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center justify-between">
            <span>🧠 Genesis2 — Creative Intelligence Engine</span>
            {result && (
              <div className="flex items-center gap-2 text-sm">
                <Badge variant={result.failedPhases === 0 ? 'success' : 'destructive'}>
                  {result.completedPhases}/{result.totalPhases} phases
                </Badge>
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Synopsis</label>
            <Textarea
              value={synopsis}
              readOnly
              className="min-h-[80px] text-sm text-muted-foreground"
            />
          </div>

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
              <p className="font-semibold mb-1">Genesis2 Pipeline Error</p>
              <p>{error}</p>
              <p className="mt-2 text-xs text-destructive/80">
                Make sure Ollama is running (<code className="bg-destructive/10 px-1 rounded">ollama serve</code>)
                then try again.
              </p>
            </div>
          )}

          <Button
            onClick={handleRun}
            disabled={isRunning || !synopsis.trim()}
            className="w-full"
          >
            {isRunning ? `Running Phase ${currentPhase}/12...` : 'Run Genesis2 Pipeline'}
          </Button>

          {isRunning && (
            <div className="space-y-2">
              <Progress value={(currentPhase / 12) * 100} className="h-2" />
              <p className="text-xs text-muted-foreground text-center">
                Phase {currentPhase}: {PHASE_NAMES[currentPhase - 1] || 'Starting...'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {result && result.phases && result.phases.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              12-Phase Pipeline Results
              <span className="text-sm font-normal text-muted-foreground ml-2">
                — {result.completedPhases} completed, {result.failedPhases} failed
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {result.phases.map((phase: Genesis2PhaseResult) => (
                <div
                  key={phase.phaseNumber}
                  className="flex items-center justify-between p-2 rounded-md bg-muted/30 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{getPhaseIcon(phase)}</span>
                    <div>
                      <span className="text-sm font-medium">
                        Phase {String(phase.phaseNumber).padStart(2, '0')}: {phase.phaseName}
                      </span>
                      <span className="text-xs text-muted-foreground ml-2">
                        {phase.draftCount} draft{phase.draftCount !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getPhaseBadge(phase)}
                    <Badge variant={phase.status === 'completed' ? 'success' : 'destructive'}>
                      {phase.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
