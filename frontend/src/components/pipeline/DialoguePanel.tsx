'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import type { DialogueResult } from '@/lib/types';

interface DialoguePanelProps {
  dialogues: DialogueResult[];
  scenes: { sceneNumber: number; title: string }[];
}

export default function DialoguePanel({
  dialogues,
  scenes,
}: DialoguePanelProps) {
  const sceneMap = new Map(
    scenes?.map((s) => [s.sceneNumber, s.title]) ?? []
  );
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Dialogue</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {dialogues.map((scene) => (
            <div key={scene.sceneNumber}>
              <h4 className="text-sm font-medium text-muted-foreground mb-3">
                Scene {scene.sceneNumber}
                {sceneMap.has(scene.sceneNumber) && (
                  <span className="ml-1">
                    — {sceneMap.get(scene.sceneNumber)}
                  </span>
                )}
              </h4>
              <div className="space-y-3">
                {scene.dialogues.map((line, i) => (
                  <div key={i} className="flex gap-3">
                    <span className="text-xs font-bold text-primary min-w-[80px] truncate">
                      {line.character}:
                    </span>
                    <div className="flex-1">
                      <p className="text-sm">{line.dialogue}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">
                        {line.emotion} · {line.delivery}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}