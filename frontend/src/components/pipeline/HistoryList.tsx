'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { formatDate } from '@/lib/utils';
import { usePipelineStore } from '@/lib/store';
import { EmptyState } from '@/components/ui/EmptyState';

export default function HistoryList() {
  const { history, loadHistory } = usePipelineStore();

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  if (history.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Stories</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {history.slice(0, 10).map((item) => (
            <Link
              key={item.id}
              href={`/pipeline/${item.id}`}
              className="flex items-center justify-between p-2 rounded hover:bg-accent transition-colors"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {item.topic}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(item.createdAt)}
                </p>
              </div>
              <Badge
                variant={
                  item.status === 'completed'
                    ? 'success'
                    : item.status === 'failed'
                      ? 'destructive'
                      : 'warning'
                }
              >
                {item.status}
              </Badge>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
