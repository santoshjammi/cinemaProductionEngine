'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs';
import type { Genesis3AnalyzeResult, Genesis3ReviewResult, Genesis3CertifyResult, Genesis3CertificateResponse } from '@/lib/api';
import * as api from '@/lib/api';

// ---------------------------------------------------------------------------
// Types for tab display
// ---------------------------------------------------------------------------

interface CompilerResult {
  compiler: string;
  status: 'pass' | 'fail' | 'warning';
  evidence: string[];
  requirements: string[];
}

interface QAResult {
  constitutionName: string;
  status: 'pass' | 'fail' | 'warning';
  findings: Array<{ requirement: string; finding: string }>;
  summary: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mapStatus(s: string): CompilerResult['status'] | QAResult['status'] {
  const lower = s.toLowerCase();
  if (['pass', 'passes', 'confirmed'].includes(lower)) return 'pass';
  if (['fail', 'fails', 'failed', 'critical'].includes(lower)) return 'fail';
  if (['warn', 'warning', 'caution'].includes(lower)) return 'warning';
  return 'pass'; // default optimistic
}

function statusBadge(status: CompilerResult['status'] | QAResult['status']) {
  switch (status) {
    case 'pass': return <Badge variant="success">✓ PASS</Badge>;
    case 'fail': return <Badge variant="destructive">✗ FAIL</Badge>;
    case 'warning': return <Badge variant="warning">! WARN</Badge>;
  }
}

function productionReadiness(status: string): 'ready' | 'not-ready' {
  return (status.toLowerCase() === 'ready' || status.toLowerCase() === 'approved') ? 'ready' : 'not-ready';
}

// ---------------------------------------------------------------------------
// Parsing helpers — accept whatever the backend returns and extract what we need
// ---------------------------------------------------------------------------

function parseCompilerResults(data: any): CompilerResult[] {
  if (!data) return [];

  // Try common shapes
  let compilers: Record<string, any> | Array<any> = data.compilersPass || data.compilers || data.results || data;

  const results: CompilerResult[] = [];

  if (Array.isArray(compilers)) {
    for (const c of compilers as any[]) {
      results.push({
        compiler: c.compiler || c.name || 'Unknown',
        status: mapStatus(c.status || c.result || ''),
        evidence: Array.isArray(c.evidence) ? c.evidence.map(String) : [String(c.evidence || '')],
        requirements: Array.isArray(c.requirements) ? c.requirements.map(String) : [String(c.name || c.rule || '')],
      });
    }
  } else if (typeof compilers === 'object') {
    for (const [name, val] of Object.entries(compilers)) {
      const entry = val as any;
      results.push({
        compiler: name,
        status: mapStatus(entry.status || entry.result || ''),
        evidence: Array.isArray(entry.evidence) ? entry.evidence.map(String) : (entry.foundations ? [entry.foundations] : ['No evidence']),
        requirements: Array.isArray(entry.requirements) ? entry.requirements.map(String) : ([entry.rule, entry.criterion].filter(Boolean)),
      });
    }
  }

  return results;
}

function parseQAReport(data: any): QAResult[] {
  if (!data) return [];

  let checks: ReadonlyArray<any> = data.reviewReport?.constitutionChecks || data.constitutionChecks || data.checks || data.findings || [];
  if (checks.length === 0 && typeof data === 'object' && !Array.isArray(data)) {
    for (const [name, val] of Object.entries(data as any)) {
      checks = [ ...(checks as any[]), { rule: name, status: (val as any)?.status || 'pass', finding: '', requirement: name } ];
    }
  }

  return (checks as Array<any>).filter(Boolean).map((c: any) => ({
    constitutionName: c.rule || c.constitution || c.name || c.requirement || 'Unknown',
    status: mapStatus(c.status || c.result || 'pass'),
    findings: [
      ...(Array.isArray(c.findings) ? c.findings : [{ requirement: c.evidence || '', finding: c.finding || c.description || '' }]),
    ].map((f: any) => ({
      requirement: f.requirement || f.rule || '',
      finding: f.finding || f.finding || f.description || '',
    })),
    summary: c.summary || c.overview || '',
  }));
}

function buildCertificate(
  res: Genesis3CertifyResult | { certificationResponse?: any; result?: any },
  reviewData?: Genesis3ReviewResult
): Genesis3CertificateResponse {
  const data = res as any;
  const raw = data?.certificationResponse || data?.result || data?.certificate || data;

  return {
    id: raw?.id || '',
    title: raw?.title || 'Production Readiness Certificate',
    synopsisSummary: raw?.synopsisSummary || raw?.summary || '',
    productionReadiness: productionReadiness(raw?.productionReadiness || raw?.status || ''),
    issuedAt: raw?.issuedAt || raw?.date || new Date().toISOString(),
    compilersPass: raw?.compilersPass || {},
    qaResult: data?.reviewResult || reviewData || (raw?.qaResult ? { qaResult: raw.qaResult } : {}),
  };
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const CertificateDisplay = ({ cert }: { cert: Genesis3CertificateResponse }) => {
  const readiness = productionReadiness(cert.productionReadiness);
  return (
    <div className="border-2 border-dashed rounded-xl p-8 text-center max-w-5xl mx-auto bg-gradient-to-b from-amber-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Crown / seal */}
      <div className="text-6xl mb-4">🏛️</div>

      <h2 className="font-display text-display-md text-ink mb-1" style={{ letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        Production Readiness Certificate
      </h2>
      <p className="text-lg text-ink-muted-80 mb-6">Official GENESIS3 Certification</p>

      <div className="border-t border-b border-amber-300 dark:border-amber-700 py-4 my-6 space-y-3">
        <p className="text-xl font-display text-ink">{cert.title}</p>
        <p className="text-body text-ink-muted-80 max-w-3xl mx-auto">
          {cert.synopsisSummary || 'SYNOPSIS UNDER REVIEW'}
        </p>
      </div>

      {/* Compilers summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-8 text-left">
        <div>
          <h3 className="text-caption-strong text-ink-muted-48 mb-2 uppercase tracking-wide">Compilers Pass</h3>
          {cert.compilersPass && Object.keys(cert.compilersPass).length > 0 ? (
            <ul className="space-y-1.5 text-sm">
              {Object.entries(cert.compilersPass).map(([k, v]: [string, any]) => (
                <li key={k} className="flex items-center gap-2">
                  <Badge variant={(v?.status || '').toLowerCase().includes('pass') ? 'success' : 'warning'}>
                    {v?.status || 'N/A'}
                  </Badge>
                  <span className="text-ink-muted-80">{k}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-ink-muted-80">No compiler results</p>
          )}
        </div>

        <div>
          <h3 className="text-caption-strong text-ink-muted-48 mb-2 uppercase tracking-wide">QA Constitution Check</h3>
          {cert.qaResult && (cert.qaResult as any).qaResult?.constitutionChecks ? (
            <ul className="space-y-1.5 text-sm">
              {Array.isArray((cert.qaResult as any).qaResult.constitutionChecks) &&
                (cert.qaResult as any).qaResult.constitutionChecks.map((c: any, i: number) => (
                  <li key={i} className="flex items-center gap-2">
                    <Badge variant={(mapStatus(c.status) === 'pass' ? 'success' : mapStatus(c.status) === 'fail' ? 'destructive' : 'warning') as any}>{c.rule || 'Constitution'}</Badge>
                  </li>
                ))}
            </ul>
          ) : (
            <p className="text-sm text-ink-muted-80">No QA results</p>
          )}
        </div>
      </div>

      {/* Verdict */}
      <div className={`inline-block rounded-full px-8 py-3 text-xl font-display ${
        readiness === 'ready'
          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-700'
          : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400 border border-red-300 dark:border-red-700'
      }`}>
        {readiness === 'ready' ? '✓ PRODUCTION READY' : '✗ NOT YET PRODUCTION READY'}
      </div>

      <p className="text-xs text-ink-muted-48 mt-8">
        Issued: {new Date(cert.issuedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        {' '}• GENESIS3 Pipeline v1.0
      </p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------

export default function Genesis3Page() {
  const [synopsis, setSynopsis] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('compilers');
  const [error, setError] = useState<string | null>(null);

  // Results state
  const [analyzeResult, setAnalyzeResult] = useState<Genesis3AnalyzeResult | null>(null);
  const [reviewResult, setReviewResult] = useState<Genesis3ReviewResult | null>(null);
  const [certifyResult, setCertifyResult] = useState<Genesis3CertifyResult | Genesis3CertificateResponse | null>(null);

  // Parsed data for display
  const compilerResults = analyzeResult ? parseCompilerResults(analyzeResult) : [];
  const qaResults = reviewResult ? parseQAReport(reviewResult) : [];
  const certDisplay = certifyResult ? buildCertificate(certifyResult as any, reviewResult ?? undefined) : null;

  // Constraint fields (can be extended later)
  const [constraints, setConstraints] = useState<api.Genesis3Constraints>({});

  const handleRun = async () => {
    if (!synopsis.trim()) return;
    setIsRunning(true);
    setError(null);
    setActiveTab('progress');

    try {
      // Run all three stages in parallel (they can be independent)
      const [analyzeData, reviewData, certifyData] = await Promise.allSettled([
        api.analyzeSynopsis(synopsis, constraints).catch(() => null),
        api.reviewSynopsis(synopsis, constraints).catch(() => null),
        api.certifySynopsis(synopsis, constraints).catch(() => null),
      ]);

      if (analyzeData.status === 'fulfilled' && analyzeData.value) setAnalyzeResult(analyzeData.value);
      if (reviewData.status === 'fulfilled' && reviewData.value) setReviewResult(reviewData.value);
      if (certifyData.status === 'fulfilled' && certifyData.value) setCertifyResult(certifyData.value);

      // Auto-select the last completed tab
      setActiveTab(certifyData.status === 'fulfilled' ? 'certificate' : reviewData.status === 'fulfilled' ? 'qa' : 'compilers');
    } catch (err: any) {
      setError(err.message || 'GENESIS3 pipeline failed');
    } finally {
      setIsRunning(false);
    }
  };

  // ---------------------------------------------------------------------------
  // Progress tab
  // ---------------------------------------------------------------------------

  const phases = [
    { name: 'Synopsis Analysis', key: 'analyze' as const },
    { name: 'Constitution Review', key: 'review' as const },
    { name: 'Certificate Generation', key: 'certify' as const },
  ];
  const hasAnalyze = !!analyzeResult;
  const hasReview = !!reviewResult;
  const hasCertify = !!certifyResult;

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-canvas py-section px-lg">
      <div className="max-w-[1200px] mx-auto space-y-8">

        {/* Header */}
        <section className="text-center space-y-4">
          <h1 className="font-display text-display-md text-ink">
            GENESIS3 — Creative Integrity Engine
          </h1>
          <p className="text-lead text-ink-muted-80 max-w-[720px] mx-auto">
            Three-stage analysis pipeline: Synopsis Analysis → Constitution Review → Production Readiness Certificate
          </p>
        </section>

        {/* Input card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <span className="text-2xl">📜</span>
              Synopsis Input
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              placeholder="Enter your film synopsis here..."
              rows={12}
              className="w-full rounded-lg border border-hairline bg-canvas-parchment px-4 py-3 text-body text-ink placeholder:text-ink-muted-48 focus:outline-none focus:ring-2 focus:ring-primary-focus resize-y"
            />

            {/* Constraints row (simple) */}
            <div className="flex flex-wrap gap-3">
              <select
                value={constraints.tone || ''}
                onChange={(e) => setConstraints({ ...constraints, tone: e.target.value || undefined })}
                className="rounded-lg border border-hairline bg-canvas-parchment px-3 py-2 text-sm text-ink outline-none focus:ring-2 focus:ring-primary-focus"
              >
                <option value="">Tone</option>
                <option value="dramatic">Dramatic</option>
                <option value="comedic">Comedic</option>
                <option value="dark">Dark</option>
                <option value="whimsical">Whimsical</option>
              </select>
              <select
                value={constraints.genre || ''}
                onChange={(e) => setConstraints({ ...constraints, genre: e.target.value || undefined })}
                className="rounded-lg border border-hairline bg-canvas-parchment px-3 py-2 text-sm text-ink outline-none focus:ring-2 focus:ring-primary-focus"
              >
                <option value="">Genre</option>
                <option value="drama">Drama</option>
                <option value="thriller">Thriller</option>
                <option value="sci-fi">Sci-Fi</option>
                <option value="fantasy">Fantasy</option>
              </select>
              <select
                value={constraints.length || ''}
                onChange={(e) => setConstraints({ ...constraints, length: e.target.value || undefined })}
                className="rounded-lg border border-hairline bg-canvas-parchment px-3 py-2 text-sm text-ink outline-none focus:ring-2 focus:ring-primary-focus"
              >
                <option value="">Length</option>
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long Feature</option>
              </select>
            </div>

            {error && (
              <p className="text-sm text-destructive p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                {error}
              </p>
            )}

            <Button
              onClick={handleRun}
              disabled={isRunning || !synopsis.trim()}
              className="w-full text-body"
              size="lg"
            >
              {isRunning ? '⏳ Running GENESIS3…' : '▶️ Run GENESIS3 Pipeline'}
            </Button>
          </CardContent>
        </Card>

        {/* Results section */}
        {(analyzeResult || reviewResult || certifyResult) && (
          <Card className="border-2 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-3 text-display-md">
                  <span className="text-2xl">🧬</span>
                  GENESIS3 Results
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">

              {/* Progress tracker */}
              {isRunning && (
                <div className="flex items-center gap-4 text-sm">
                  {phases.map((p, i) => {
                    const done = [hasAnalyze, hasReview, hasCertify][i];
                    return (
                      <div key={p.key} className="flex items-center gap-2">
                        <span className={`w-8 h-8 flex items-center justify-center rounded-full text-sm ${
                          done
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                            : isRunning
                              ? 'bg-gray-100 text-gray-400 border border-gray-200'
                              : 'bg-gray-50 text-gray-300 border border-gray-200'
                        }`}>
                          {done ? '✓' : (i + 1)}
                        </span>
                        <span className="text-ink-muted-80">{p.name}</span>
                        {i < phases.length - 1 && (
                          <div className={`w-12 h-[2px] ${
                            i === 0 ? 'bg-gray-200' : done ? 'bg-emerald-300' : 'bg-gray-100'
                          }`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Tabs */}
              <Tabs value={isRunning ? 'progress' : activeTab} onValueChange={(v) => !isRunning && setActiveTab(v)}>
                <TabsList>
                  <TabsTrigger value="compilers" disabled={isRunning || compilerResults.length === 0}>
                    🔬 Compilers
                    {compilerResults.length > 0 ? ` (${compilerResults.length})` : ''}
                  </TabsTrigger>
                  <TabsTrigger value="qa" disabled={isRunning || qaResults.length === 0}>
                    ⚖️ QA Report
                    {qaResults.length > 0 ? ` (${qaResults.length})` : ''}
                  </TabsTrigger>
                  <TabsTrigger value="certificate" disabled={isRunning || !certDisplay}>
                    🏛️ Certificate
                  </TabsTrigger>
                </TabsList>

                {/* Compilers tab */}
                <TabsContent value="compilers">
                  {compilerResults.length > 0 ? (
                    <div className="space-y-4">
                      {compilerResults.map((r, i) => (
                        <div key={i} className="border border-hairline rounded-lg p-5 bg-canvas-parchment/60">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="text-body font-medium text-ink">{r.compiler}</h4>
                            {statusBadge(r.status)}
                          </div>

                          {/* Requirements */}
                          <div className="mb-3">
                            <span className="text-xs uppercase tracking-wider text-ink-muted-48">Requirements:</span>
                            <ul className="text-sm text-ink-muted-80 mt-1 space-y-0.5">
                              {r.requirements.map((req, j) => (
                                <li key={j}>{req}</li>
                              ))}
                            </ul>
                          </div>

                          {/* Evidence */}
                          <details className="mt-2">
                            <summary className="text-xs cursor-pointer text-primary hover:underline">
                              View {r.evidence.length} evidence item{r.evidence.length !== 1 ? 's' : ''}
                            </summary>
                            <ul className="text-sm text-ink-muted-80 mt-1 ml-3 space-y-1 list-disc">
                              {r.evidence.map((ev, j) => (
                                <li key={j}>{ev}</li>
                              ))}
                            </ul>
                          </details>
                        </div>
                      ))}

                      {/* Overall verdict */}
                      <div className={`text-center p-4 rounded-lg ${
                        compilerResults.every(r => r.status === 'pass')
                          ? 'bg-emerald-50 border border-emerald-200'
                          : compilerResults.some(r => r.status === 'warning')
                            ? 'bg-amber-50 border border-amber-200'
                            : 'bg-red-50 border border-red-200'
                      }`}>
                        <p className={`text-body font-display ${
                          compilerResults.every(r => r.status === 'pass')
                            ? 'text-emerald-700'
                            : compilerResults.some(r => r.status === 'warning')
                              ? 'text-amber-700'
                              : 'text-red-700'
                        }`}>
                          {compilerResults.every(r => r.status === 'pass')
                            ? `✓ All ${compilerResults.length} compilers PASSED`
                            : compilerResults.some(r => r.status === 'fail')
                              ? `${compilerResults.filter(r => r.status === 'fail').length} COMPILER(S) FAILED`
                              : `${compilerResults.filter(r => r.status === 'warning').length} COMPILER(S) WARNING`}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-ink-muted-80">
                      No compiler results available. Run the pipeline to get results.
                    </div>
                  )}
                </TabsContent>

                {/* QA Report tab */}
                <TabsContent value="qa">
                  {qaResults.length > 0 ? (
                    <div className="space-y-4">
                      {qaResults.map((qa, i) => (
                        <div key={i} className="border border-hairline rounded-lg p-5 bg-canvas-parchment/60">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="text-body font-medium text-ink">{qa.constitutionName}</h4>
                            {statusBadge(qa.status)}
                          </div>

                          {qa.summary && (
                            <p className="text-sm text-ink-muted-80 mb-3">{qa.summary}</p>
                          )}

                          {/* Findings */}
                          {qa.findings.length > 0 && (
                            <details className="mt-2">
                              <summary className="text-xs cursor-pointer text-primary hover:underline">
                                View {qa.findings.length} finding{qa.findings.length !== 1 ? 's' : ''}
                              </summary>
                              <div className="text-sm text-ink-muted-80 mt-2 space-y-2 ml-3">
                                {qa.findings.map((f, j) => (
                                  <div key={j} className="border-l-2 border-primary/20 pl-3">
                                    <span className="font-medium text-ink">Requirement: </span>
                                    <span>{f.requirement || '—'}</span>
                                    <br />
                                    <span className="font-medium text-ink">Finding: </span>
                                    <span>{f.finding || '—'}</span>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      ))}

                      {(() => {
                        const passCount = qaResults.filter(q => q.status === 'pass').length;
                        const totalCount = qaResults.length;
                        return (
                          <div className={`text-center p-4 rounded-lg ${
                            qaResults.every(r => r.status === 'pass')
                              ? 'bg-emerald-50 border border-emerald-200'
                              : 'bg-red-50 border border-red-200'
                          }`}>
                            <p className={`text-body font-display ${
                              qaResults.every(r => r.status === 'pass')
                                ? 'text-emerald-700'
                                : 'text-red-700'
                            }`}>
                              {qaResults.every(r => r.status === 'pass')
                                ? `✓ All ${totalCount} constitution checks PASSED`
                                : `${totalCount - passCount} of ${totalCount} constitution checks FAILED`}
                            </p>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-ink-muted-80">
                      No QA results available. Run the pipeline to get results.
                    </div>
                  )}
                </TabsContent>

                {/* Certificate tab */}
                <TabsContent value="certificate">
                  {certDisplay ? (
                    <CertificateDisplay cert={certDisplay} />
                  ) : (
                    <div className="text-center py-12 text-ink-muted-80">
                      <p className="text-xl mb-4">📋</p>
                      <p>Certificate not generated yet.</p>
                      <p className="text-sm mt-2">Run the full pipeline to produce a Production Readiness Certificate.</p>
                    </div>
                  )}
                </TabsContent>

                {/* Progress tab */}
                <TabsContent value="progress">
                  <div className="space-y-4 py-8 text-center">
                    <div className="inline-block w-12 h-12 border-4 border-primary/20 border-t-primary animate-spin rounded-full" />
                    <p className="text-body text-ink-muted-80">Running GENESIS3 pipeline…</p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {/* Empty state */}
        {!analyzeResult && !reviewResult && !certifyResult && !isRunning && (
          <div className="text-center py-16 text-ink-muted-40">
            <p className="text-4xl mb-4">✍️</p>
            <p className="text-body max-w-md mx-auto">
              Enter a synopsis above and click &quot;Run GENESIS3 Pipeline&quot; to analyze your story.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
