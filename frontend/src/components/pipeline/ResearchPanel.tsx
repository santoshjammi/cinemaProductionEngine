'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ExternalLink } from 'lucide-react';
import type { ResearchResult } from '@/lib/types';

interface ResearchPanelProps {
  research: ResearchResult;
}

export default function ResearchPanel({ research }: ResearchPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-blue-500" />
          Internet Research
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-1">
            Summary
          </h4>
          <p className="text-sm">{research.summary}</p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            Key Findings
          </h4>
          <ul className="space-y-1">
            {research.keyFindings.map((finding, i) => (
              <li
                key={i}
                className="text-sm flex items-start gap-2"
              >
                <span className="text-blue-500 mt-1">•</span>
                {finding}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-medium text-muted-foreground mb-2">
            Sources
          </h4>
          <div className="space-y-2">
            {research.sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-2 text-sm text-primary hover:underline group"
              >
                <ExternalLink className="w-3 h-3 mt-0.5 shrink-0" />
                <span className="flex-1">{source.title}</span>
              </a>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}