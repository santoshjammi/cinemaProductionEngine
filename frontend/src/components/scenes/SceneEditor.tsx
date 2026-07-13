'use client';

import { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { Badge } from '@/components/ui/Badge';
import { Edit2, Save, X } from 'lucide-react';
import type { SceneResult, PromptResult } from '@/lib/types';

interface SceneEditorProps {
  scene: SceneResult;
  prompt?: PromptResult;
  onSave?: (scene: SceneResult, prompt?: PromptResult) => void;
}

export default function SceneEditor({
  scene,
  prompt,
  onSave,
}: SceneEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedScene, setEditedScene] = useState<SceneResult>({ ...scene });
  const [editedPrompt, setEditedPrompt] = useState<PromptResult | undefined>(
    prompt ? { ...prompt } : undefined
  );

  const handleSave = () => {
    onSave?.(editedScene, editedPrompt);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedScene({ ...scene });
    setEditedPrompt(prompt ? { ...prompt } : undefined);
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold">
                {scene.sceneNumber}
              </span>
              <CardTitle className="text-lg">{scene.title}</CardTitle>
            </div>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsEditing(true)}
            >
              <Edit2 className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">{scene.description}</p>
          <div className="flex flex-wrap gap-1">
            <Badge variant="secondary">{scene.location}</Badge>
            <Badge variant="outline">{scene.emotionalBeat}</Badge>
            <Badge variant="outline">{scene.duration}</Badge>
          </div>
          {scene.characters.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {scene.characters.map((char, i) => (
                <Badge key={i} variant="secondary">
                  {char}
                </Badge>
              ))}
            </div>
          )}
          {editedPrompt && (
            <div className="pt-2 border-t space-y-1">
              <p className="text-xs text-muted-foreground">
                <span className="font-medium">Style:</span> {editedPrompt.visualStyle}
                {' | '}
                <span className="font-medium">Camera:</span> {editedPrompt.cameraAngle}
                {' | '}
                <span className="font-medium">Lighting:</span> {editedPrompt.lighting}
              </p>
              <p className="text-xs text-muted-foreground line-clamp-2">
                {editedPrompt.cinematicPrompt}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">
            Edit Scene {scene.sceneNumber}
          </CardTitle>
          <div className="flex gap-2">
            <Button size="sm" variant="ghost" onClick={handleCancel}>
              <X className="w-4 h-4" />
            </Button>
            <Button size="sm" onClick={handleSave}>
              <Save className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Title</label>
          <Input
            value={editedScene.title}
            onChange={(e) =>
              setEditedScene({ ...editedScene, title: e.target.value })
            }
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Description</label>
          <Textarea
            rows={3}
            value={editedScene.description}
            onChange={(e) =>
              setEditedScene({ ...editedScene, description: e.target.value })
            }
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Location</label>
            <Input
              value={editedScene.location}
              onChange={(e) =>
                setEditedScene({ ...editedScene, location: e.target.value })
              }
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Duration</label>
            <Input
              value={editedScene.duration}
              onChange={(e) =>
                setEditedScene({ ...editedScene, duration: e.target.value })
              }
            />
          </div>
        </div>

        {editedPrompt && (
          <>
            <div className="border-t pt-4 space-y-3">
              <h4 className="text-sm font-medium">Cinematic Settings</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Visual Style</label>
                  <Input
                    value={editedPrompt.visualStyle}
                    onChange={(e) =>
                      setEditedPrompt({
                        ...editedPrompt,
                        visualStyle: e.target.value,
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Camera Angle</label>
                  <Input
                    value={editedPrompt.cameraAngle}
                    onChange={(e) =>
                      setEditedPrompt({
                        ...editedPrompt,
                        cameraAngle: e.target.value,
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Lighting</label>
                  <Input
                    value={editedPrompt.lighting}
                    onChange={(e) =>
                      setEditedPrompt({
                        ...editedPrompt,
                        lighting: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Cinematic Prompt
                </label>
                <Textarea
                  rows={3}
                  value={editedPrompt.cinematicPrompt}
                  onChange={(e) =>
                    setEditedPrompt({
                      ...editedPrompt,
                      cinematicPrompt: e.target.value,
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Color Palette</label>
                <div className="flex gap-1">
                  {editedPrompt.colorPalette.map((color, i) => (
                    <Badge key={i} variant="outline">
                      {color}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
