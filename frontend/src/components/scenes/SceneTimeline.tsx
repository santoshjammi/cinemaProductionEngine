'use client';

import { useState } from 'react';
import SceneCard from './SceneCard';
import type { SceneResult, PromptResult } from '@/lib/types';

interface SceneTimelineProps {
  scenes: SceneResult[];
  prompts?: PromptResult[];
  onSceneSelect?: (sceneNumber: number) => void;
}

export default function SceneTimeline({
  scenes,
  prompts,
  onSceneSelect,
}: SceneTimelineProps) {
  const [selectedScene, setSelectedScene] = useState<number | null>(null);
  const promptMap = new Map(
    prompts?.map((p) => [p.sceneNumber, p]) ?? []
  );

  const handleSceneClick = (sceneNumber: number) => {
    setSelectedScene(sceneNumber);
    onSceneSelect?.(sceneNumber);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Scene Timeline
          <span className="text-sm font-normal text-muted-foreground ml-2">
            ({scenes.length} scenes)
          </span>
        </h3>
      </div>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {scenes.map((scene) => {
          const prompt = promptMap.get(scene.sceneNumber);
          return (
            <SceneCard
              key={scene.sceneNumber}
              sceneNumber={scene.sceneNumber}
              title={scene.title}
              description={scene.description}
              location={scene.location}
              characters={scene.characters}
              emotionalBeat={scene.emotionalBeat}
              duration={scene.duration}
              cinematicPrompt={prompt?.cinematicPrompt}
              visualStyle={prompt?.visualStyle}
              cameraAngle={prompt?.cameraAngle}
              isActive={selectedScene === scene.sceneNumber}
              onClick={() => handleSceneClick(scene.sceneNumber)}
            />
          );
        })}
      </div>
    </div>
  );
}