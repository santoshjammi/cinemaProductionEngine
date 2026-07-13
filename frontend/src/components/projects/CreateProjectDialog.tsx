'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/Dialog';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';
import { PlusIcon } from 'lucide-react';
import { usePipelineStore } from '@/lib/store';
import type { ProjectCreate } from '@/lib/types';

export function CreateProjectDialog() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const { createProject } = usePipelineStore();

  const handleSubmit = async () => {
    if (!name.trim()) return;
    await createProject({ name: name.trim(), description: description.trim() });
    setName('');
    setDescription('');
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusIcon className="w-4 h-4 mr-1" />
          New Project
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Project</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 pt-2">
          <Input
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
          />
          <Button onClick={handleSubmit} disabled={!name.trim()} className="w-full">
            Create
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
