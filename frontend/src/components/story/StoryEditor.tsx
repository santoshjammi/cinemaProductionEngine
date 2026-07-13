'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Edit2, Save, X } from 'lucide-react';
import type { StoryResult } from '@/lib/types';

interface StoryEditorProps {
  story: StoryResult;
  onSave?: (story: StoryResult) => void;
}

export default function StoryEditor({ story, onSave }: StoryEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedStory, setEditedStory] = useState<StoryResult>({ ...story });

  const handleSave = () => {
    onSave?.(editedStory);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedStory({ ...story });
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-xl">{story.title}</CardTitle>
              <p className="text-sm text-muted-foreground mt-1 italic">
                {story.logline}
              </p>
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
        <CardContent className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-muted-foreground mb-1">
              Synopsis
            </h4>
            <p className="text-sm leading-relaxed">{story.synopsis}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">{story.emotionalTone}</Badge>
            {story.themes.map((theme, i) => (
              <Badge key={i} variant="outline">
                {theme}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Edit Story</CardTitle>
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
            value={editedStory.title}
            onChange={(e) =>
              setEditedStory({ ...editedStory, title: e.target.value })
            }
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Logline</label>
          <Input
            value={editedStory.logline}
            onChange={(e) =>
              setEditedStory({ ...editedStory, logline: e.target.value })
            }
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Synopsis</label>
          <Textarea
            rows={6}
            value={editedStory.synopsis}
            onChange={(e) =>
              setEditedStory({ ...editedStory, synopsis: e.target.value })
            }
          />
        </div>
      </CardContent>
    </Card>
  );
}