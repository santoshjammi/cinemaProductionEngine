'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Textarea } from '@/components/ui/Textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { EmptyState } from '@/components/ui/EmptyState';
import { ClapperboardIcon, PlayIcon, RefreshCwIcon } from 'lucide-react';
import * as api from '@/lib/api';
import type { ProductionJob } from '@/lib/api';

const DEFAULT_SYNOPSIS = `After losing his job, a husband named Mark becomes terrified that his wife Sarah will eventually see him as a failure. Instead of admitting the fear, he slowly withdraws — short answers at dinner, avoiding eye contact, sleeping in another room, rejecting small moments of affection. His wife initially thinks he no longer loves her. The emotional turning point comes when she quietly says, "You don't have to disappear just because you're hurting." He almost responds, but fear wins for one more moment — until he finally reaches for her hand.`;

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

const STAGE_LABELS: Record<string, string> = {
  queued: 'Queued',
  policy: 'Resolving policy',
  genesis: 'GENESIS2 (12 phases)',
  bridge: 'Bridging to brief',
  prometheus: 'PROMETHEUS render',
  film: 'Assembling film',
  done: 'Done',
};

function statusBadge(status: string) {
  switch (status) {
    case 'completed': return <Badge variant="success">✓ Completed</Badge>;
    case 'failed': return <Badge variant="destructive">✗ Failed</Badge>;
    case 'running': return <Badge variant="warning">⏳ Running</Badge>;
    case 'queued': return <Badge variant="outline">Queued</Badge>;
    default: return <Badge variant="outline">{status}</Badge>;
  }
}

function JobCard({ job, onRefresh }: { job: ProductionJob; onRefresh: () => void }) {
  const isActive = job.status === 'running' || job.status === 'queued';
  const phaseProgress = job.phases.length > 0
    ? Math.round((job.phases.filter((p) => p.status === 'completed').length / 12) * 100)
    : 0;

  return (
    <Card className="border-2 border-primary/10">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          <span className="flex items-center gap-2">
            <ClapperboardIcon className="w-4 h-4" />
            Production {job.jobId.slice(0, 8)}
          </span>
          <div className="flex items-center gap-2">
            {statusBadge(job.status)}
            <Button variant="ghost" size="sm" onClick={onRefresh} title="Refresh">
              <RefreshCwIcon className="w-3.5 h-3.5" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>Stage:</span>
          <Badge variant="outline">{STAGE_LABELS[job.stage] || job.stage}</Badge>
          {job.runId && <span className="text-xs">· {job.runId}</span>}
        </div>

        {isActive && (
          <div className="space-y-2">
            <Progress value={phaseProgress} className="h-2" />
            <p className="text-xs text-muted-foreground">
              {job.phases.length > 0
                ? `GENESIS2: ${job.phases.filter((p) => p.status === 'completed').length}/12 phases`
                : 'Starting…'}
            </p>
          </div>
        )}

        {job.phases.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
            {job.phases.map((p) => (
              <div key={p.phaseNumber} className="flex items-center gap-1.5 text-xs">
                <span>{p.status === 'completed' ? '✅' : p.status === 'failed' ? '❌' : '⏳'}</span>
                <span className="text-muted-foreground truncate">{p.phaseName}</span>
              </div>
            ))}
          </div>
        )}

        {job.prometheusStages.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {job.prometheusStages.map((s) => (
              <Badge key={s.name} variant={s.status === 'completed' ? 'success' : s.status === 'failed' ? 'destructive' : 'outline'}>
                {s.name} ({s.artifacts})
              </Badge>
            ))}
          </div>
        )}

        {job.error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
            {job.error}
          </div>
        )}

        {job.status === 'completed' && job.outputPath && (
          <div className="space-y-2">
            <video
              controls
              className="w-full rounded-lg border border-hairline bg-black"
              src={api.getProductionVideoUrl(job.jobId)}
            />
            <p className="text-xs text-muted-foreground break-all">{job.outputPath}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function ProductionPage() {
  const [synopsis, setSynopsis] = useState(DEFAULT_SYNOPSIS);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('new');
  const [jobs, setJobs] = useState<ProductionJob[]>([]);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadJobs = async () => {
    try {
      const list = await api.listProductionJobs();
      setJobs(list);
    } catch { /* silent */ }
  };

  useEffect(() => {
    loadJobs();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  // Poll active jobs every 5s
  useEffect(() => {
    const hasActive = jobs.some((j) => j.status === 'running' || j.status === 'queued');
    if (hasActive && !pollRef.current) {
      pollRef.current = setInterval(loadJobs, 5000);
    } else if (!hasActive && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, [jobs]);

  const handleSubmit = async () => {
    if (!synopsis.trim()) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const job = await api.startProduction({ synopsis });
      setJobs((prev) => [job, ...prev]);
      setActiveTab('jobs');
    } catch (err: any) {
      setError(err.message || 'Failed to start production');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container py-8 space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Production Studio</h1>
          <p className="text-muted-foreground mt-1">
            Synopsis → GENESIS2 → PROMETHEUS → final MP4. The canonical end-to-end film pipeline.
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="new">New Production</TabsTrigger>
            <TabsTrigger value="jobs">
              Jobs {jobs.length > 0 ? `(${jobs.length})` : ''}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="new" className="space-y-6 mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <span className="text-2xl">🎬</span>
                  Start a Production
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Synopsis</label>
                  <Textarea
                    value={synopsis}
                    onChange={(e) => setSynopsis(e.target.value)}
                    rows={12}
                    placeholder="Enter your film synopsis…"
                    className="min-h-[200px]"
                  />
                </div>

                {error && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
                    {error}
                  </div>
                )}

                <Button onClick={handleSubmit} disabled={isSubmitting || !synopsis.trim()} className="w-full" size="lg">
                  {isSubmitting ? '⏳ Queuing…' : '▶️ Start Production'}
                </Button>
                <p className="text-xs text-muted-foreground text-center">
                  Runs the full 12-phase GENESIS2 + PROMETHEUS pipeline locally. Takes several minutes.
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="jobs" className="space-y-6 mt-6">
            {jobs.length === 0 ? (
              <EmptyState
                icon={<ClapperboardIcon className="w-12 h-12" />}
                title="No productions yet"
                description="Start a production to generate your first film."
              />
            ) : (
              <div className="space-y-6">
                {jobs.map((job) => (
                  <JobCard key={job.jobId} job={job} onRefresh={loadJobs} />
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
