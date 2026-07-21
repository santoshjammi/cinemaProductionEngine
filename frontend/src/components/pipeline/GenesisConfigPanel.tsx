'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Progress } from '@/components/ui/Progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import type { GenesisResult, GenesisSpecGroup, GenesisSpecField } from '@/lib/types';
import * as api from '@/lib/api';

interface GenesisConfigPanelProps {
  synopsis: string;
  onGenesisComplete: (result: GenesisResult) => void;
  onApplyToPipeline: (specs: GenesisSpecGroup[]) => void;
}

export default function GenesisConfigPanel({
  synopsis,
  onGenesisComplete,
  onApplyToPipeline,
}: GenesisConfigPanelProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<GenesisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeSpec, setActiveSpec] = useState<string | null>(null);
  const [editedFields, setEditedFields] = useState<Record<string, Record<string, any>>>({});

  const handleRunGenesis = async () => {
    if (!synopsis.trim()) return;
    setIsRunning(true);
    setError(null);
    try {
      const data = await api.runGenesis(synopsis);
      setResult(data);
      onGenesisComplete(data);
    } catch (err: any) {
      setError(err.message || 'Genesis pipeline failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleFieldChange = (specId: string, fieldKey: string, value: any) => {
    setEditedFields((prev) => ({
      ...prev,
      [specId]: {
        ...(prev[specId] || {}),
        [fieldKey]: value,
      },
    }));
  };

  const handleApply = () => {
    if (!result) return;
    // Merge edited fields into specs
    const mergedSpecs = result.specs.map((spec) => {
      const edits = editedFields[spec.specId];
      if (!edits) return spec;
      return {
        ...spec,
        fields: spec.fields.map((f) => ({
          ...f,
          value: edits[f.key] !== undefined ? edits[f.key] : f.value,
        })),
      };
    });
    onApplyToPipeline(mergedSpecs);
  };

  const getFieldValue = (spec: GenesisSpecGroup, field: GenesisSpecField) => {
    const edits = editedFields[spec.specId];
    if (edits && edits[field.key] !== undefined) return edits[field.key];
    return field.value;
  };

  const renderField = (spec: GenesisSpecGroup, field: GenesisSpecField) => {
    const value = getFieldValue(spec, field);
    const onChange = (v: any) => handleFieldChange(spec.specId, field.key, v);

    switch (field.type) {
      case 'textarea':
        return (
          <Textarea
            value={typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value)}
            className="min-h-[80px] text-xs font-mono"
          />
        );
      case 'select':
        return (
          <select
            value={String(value)}
            onChange={(e) => onChange(e.target.value)}
            className="w-full h-9 px-3 py-2 text-sm border rounded-md bg-background"
          >
            {field.options?.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        );
      case 'array':
        return (
          <Textarea
            value={Array.isArray(value) ? value.join('\n') : String(value)}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
              onChange(e.target.value.split('\n').filter(Boolean))
            }
            className="min-h-[60px] text-xs font-mono"
          />
        );
      case 'object':
        return (
          <Textarea
            value={typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
              try { onChange(JSON.parse(e.target.value)); }
              catch { onChange(e.target.value); }
            }}
            className="min-h-[100px] text-xs font-mono"
          />
        );
      default:
        return (
          <Input
            value={String(value || '')}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
          />
        );
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center justify-between">
            <span>Genesis — Pre-Production Intelligence</span>
            {result && (
              <div className="flex items-center gap-2 text-sm">
                <Badge variant={result.gatePassed ? 'success' : 'destructive'}>
                  Gate: {result.gatePassed ? 'PASSED' : 'FAILED'}
                </Badge>
                <span className="text-muted-foreground">
                  {Math.round(result.completeness * 100)}% complete
                </span>
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
              className="min-h-[100px] text-sm text-muted-foreground"
            />
          </div>

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm text-destructive">
              <p className="font-semibold mb-1">Genesis Pipeline Error</p>
              <p>{error}</p>
              <p className="mt-2 text-xs text-destructive/80">
                Make sure Ollama is running (<code className="bg-destructive/10 px-1 rounded">ollama serve</code>) 
                or LMStudio is running on port 1234, then try again.
              </p>
            </div>
          )}

          <Button
            onClick={handleRunGenesis}
            disabled={isRunning || !synopsis.trim()}
            className="w-full"
          >
            {isRunning ? 'Running 31 Genesis Agents...' : 'Run Genesis Pipeline'}
          </Button>

          {isRunning && (
            <Progress value={50} className="h-2" />
          )}
        </CardContent>
      </Card>

      {result && result.specs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              Generated Specifications ({result.specs.length})
              <span className="text-sm font-normal text-muted-foreground ml-2">
                — Edit values below, then apply to pipeline
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeSpec || result.specs[0]?.specId} onValueChange={setActiveSpec}>
              <TabsList className="flex-wrap h-auto">
                {result.specs.map((spec) => (
                  <TabsTrigger key={spec.specId} value={spec.specId} className="text-xs">
                    {spec.specId}
                  </TabsTrigger>
                ))}
              </TabsList>

              {result.specs.map((spec) => (
                <TabsContent key={spec.specId} value={spec.specId} className="space-y-3 mt-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Badge variant="outline">{spec.phase}</Badge>
                    <span>Confidence: {spec.confidence}</span>
                    <Badge variant={spec.validationStatus === 'passed' ? 'success' : 'warning'}>
                      {spec.validationStatus}
                    </Badge>
                  </div>

                  {spec.fields.length === 0 && (
                    <div className="text-sm text-muted-foreground italic">
                      Detailed fields available after real LLM run. Mock mode provides summary only.
                    </div>
                  )}

                  {spec.fields.map((field) => (
                    <div key={field.key} className="space-y-1">
                      <label className="text-xs font-medium text-muted-foreground">
                        {field.label}
                        {field.description && (
                          <span className="font-normal ml-1">— {field.description}</span>
                        )}
                      </label>
                      {renderField(spec, field)}
                    </div>
                  ))}
                </TabsContent>
              ))}
            </Tabs>

            <div className="mt-6 flex justify-end">
              <Button onClick={handleApply}>
                Apply to Pipeline
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
