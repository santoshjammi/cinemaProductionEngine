'use client';

import React, { useState, useEffect } from 'react';
import StoryInput from './StoryInput';
import StageIndicator from './StageIndicator';
import StoryViewer from '@/components/story/StoryViewer';
import ResearchPanel from './ResearchPanel';
import SceneTimeline from '@/components/scenes/SceneTimeline';
import DialoguePanel from './DialoguePanel';
import MetricsPanel from './MetricsPanel';
import ClipGenerator from '@/components/video/ClipGenerator';
import VideoPlayer from '@/components/video/VideoPlayer';
import ImageGallery from '@/components/scenes/ImageGallery';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { SkeletonCard } from '@/components/ui/LoadingSkeleton';
import { Button } from '@/components/ui/Button';
import { getOverallProgress } from '@/lib/utils';
import { usePipelineStore } from '@/lib/store';
import type {
  PipelineStageName,
  SceneResult,
  DialogueResult,
  PromptResult,
} from '@/lib/types';

type VideoMode = 'svd' | 'ken-burns';

interface PipelineViewProps {
  projectId?: string;
}

export default function PipelineView({ projectId }: PipelineViewProps) {
  const {
    currentPipeline,
    generationProgress,
    sceneImages,
    isRunning,
    isImageGenRunning,
    startPipeline,
    pollStatus,
    retryStage,
    startVideoGen,
    startKenBurnsGen,
    startImageGen,
    pollVideoGen,
    reset,
  } = usePipelineStore();

  const [activeTab, setActiveTab] = useState('input');
  const [selectedScene, setSelectedScene] = useState<number | null>(null);
  const [videoMode, setVideoMode] = useState<VideoMode>('ken-burns');

  useEffect(() => {
    if (currentPipeline?.id && currentPipeline.status === 'running') {
      pollStatus(currentPipeline.id);
    }
  }, [currentPipeline?.id]);

  useEffect(() => {
    if (currentPipeline?.status === 'completed') {
      setActiveTab('story');
    }
  }, [currentPipeline?.status]);

  const handleStart = async (input: Parameters<typeof startPipeline>[0]) => {
    await startPipeline(input, projectId);
  };

  const handleStageRetry = async (stage: PipelineStageName) => {
    await retryStage(stage);
  };

  const handleGenerateClips = async () => {
    if (videoMode === 'ken-burns') {
      await startKenBurnsGen();
    } else {
      await startVideoGen();
    }
  };

  const handleGenerateImages = async () => {
    await startImageGen();
  };

  const pipeline = currentPipeline;
  const progress = generationProgress;
  const overallProgress = pipeline
    ? getOverallProgress(pipeline.stages)
    : 0;

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="input">Input</TabsTrigger>
          <TabsTrigger
            value="story"
            disabled={!pipeline?.story}
          >
            Story
          </TabsTrigger>
          <TabsTrigger
            value="scenes"
            disabled={!pipeline?.scenes}
          >
            Scenes
          </TabsTrigger>
          <TabsTrigger
            value="images"
            disabled={!pipeline?.prompts}
          >
            Images
          </TabsTrigger>
          <TabsTrigger
            value="video"
            disabled={!pipeline?.scenes}
          >
            Video
          </TabsTrigger>
        </TabsList>

        <TabsContent value="input" className="space-y-6 mt-6">
          <StoryInput onStart={handleStart} isLoading={isRunning} />

          {pipeline && pipeline.status === 'running' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  Pipeline Progress — {overallProgress}%
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="h-2 rounded-full bg-secondary overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-500 ease-in-out"
                    style={{ width: `${overallProgress}%` }}
                  />
                </div>
                <StageIndicator
                  stages={pipeline.stages}
                  currentStage={
                    pipeline.stages.find((s) => s.status === 'running')?.name
                  }
                  onStageClick={handleStageRetry}
                />
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="story" className="space-y-6 mt-6">
          {pipeline && (
            <>
              <StageIndicator
                stages={pipeline.stages}
                onStageClick={handleStageRetry}
              />

              <div className="grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-2 space-y-6">
                  {pipeline.research && (
                    <ResearchPanel research={pipeline.research} />
                  )}
                  {pipeline.story && (
                    <StoryViewer story={pipeline.story} />
                  )}
                  {pipeline.dialogues && pipeline.scenes && (
                    <DialoguePanel
                      dialogues={pipeline.dialogues}
                      scenes={pipeline.scenes}
                    />
                  )}
                </div>

                <div className="space-y-6">
                  {pipeline.metrics && (
                    <MetricsPanel metrics={pipeline.metrics} />
                  )}
                </div>
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="scenes" className="space-y-6 mt-6">
          {pipeline?.scenes && (
            <>
              <StageIndicator
                stages={pipeline.stages}
                onStageClick={handleStageRetry}
              />
              <SceneTimeline
                scenes={pipeline.scenes}
                prompts={pipeline.prompts}
                onSceneSelect={setSelectedScene}
              />
            </>
          )}
        </TabsContent>

        <TabsContent value="images" className="space-y-6 mt-6">
          {pipeline?.scenes && pipeline?.prompts && (
            <ImageGallery
              scenes={pipeline.scenes as SceneResult[]}
              images={sceneImages}
              isGenerating={isImageGenRunning}
              onGenerateAll={handleGenerateImages}
            />
          )}
          {!pipeline?.prompts && (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground">
                Complete the pipeline to generate scene images
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="video" className="space-y-6 mt-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Video Mode:</span>
                <div className="flex rounded-md border overflow-hidden">
                  <button
                    onClick={() => setVideoMode('ken-burns')}
                    className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                      videoMode === 'ken-burns'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-background text-muted-foreground hover:bg-muted'
                    }`}
                  >
                    Image-based (Ken Burns)
                  </button>
                  <button
                    onClick={() => setVideoMode('svd')}
                    className={`px-3 py-1.5 text-xs font-medium transition-colors ${
                      videoMode === 'svd'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-background text-muted-foreground hover:bg-muted'
                    }`}
                  >
                    AI Motion (SVD-XT)
                  </button>
                </div>
                {videoMode === 'svd' && (
                  <span className="text-[10px] text-muted-foreground ml-2">
                    Requires SVD-XT model (~15GB)
                  </span>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 space-y-6">
              <VideoPlayer
                finalVideo={progress?.finalVideo ?? null}
                clips={progress?.clips ?? []}
                onGenerate={handleGenerateClips}
                isGenerating={
                  progress?.clips?.some(
                    (c) => c.status === 'generating'
                  ) ?? false
                }
              />
            </div>
            <div className="space-y-6">
              <ClipGenerator
                clips={progress?.clips ?? []}
                onGenerateAll={handleGenerateClips}
                isGenerating={
                  progress?.clips?.some(
                    (c) => c.status === 'generating'
                  ) ?? false
                }
              />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
