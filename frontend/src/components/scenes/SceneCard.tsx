'use client';

import { cn } from '@/lib/utils';

interface SceneCardProps {
  sceneNumber: number;
  title: string;
  description: string;
  location: string;
  characters: string[];
  emotionalBeat: string;
  duration: string;
  cinematicPrompt?: string;
  visualStyle?: string;
  cameraAngle?: string;
  isActive?: boolean;
  onClick?: () => void;
}

export default function SceneCard({
  sceneNumber,
  title,
  description,
  location,
  characters,
  emotionalBeat,
  duration,
  cinematicPrompt,
  visualStyle,
  cameraAngle,
  isActive,
  onClick,
}: SceneCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left rounded-lg border p-4 transition-all hover:shadow-md',
        isActive
          ? 'border-primary bg-primary/5 shadow-sm'
          : 'border-border bg-card'
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold">
            {sceneNumber}
          </span>
          <h4 className="font-medium text-sm">{title}</h4>
        </div>
        <span className="text-xs text-muted-foreground">{duration}</span>
      </div>

      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
        {description}
      </p>

      <div className="flex flex-wrap gap-1 mb-1">
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground">
          {location}
        </span>
        {characters.map((char, i) => (
          <span
            key={i}
            className="text-[10px] px-1.5 py-0.5 rounded bg-accent text-accent-foreground"
          >
            {char}
          </span>
        ))}
      </div>

      <span className="text-[10px] italic text-muted-foreground">
        {emotionalBeat}
      </span>

      {cinematicPrompt && (
        <div className="mt-2 pt-2 border-t text-[10px] text-muted-foreground space-y-0.5">
          {visualStyle && <p>Style: {visualStyle}</p>}
          {cameraAngle && <p>Camera: {cameraAngle}</p>}
        </div>
      )}
    </button>
  );
}