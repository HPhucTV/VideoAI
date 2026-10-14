import { z } from "zod";

export const CanvasSchema = z.object({
  width: z.number().int().positive().default(1080),
  height: z.number().int().positive().default(1920),
  fps: z.number().int().positive().default(30),
});

export const VoiceConfigSchema = z.object({
  provider: z.enum(["edge-tts", "vbee", "lucylab", "elevenlabs"]).default("edge-tts"),
  voiceId: z.string().default("vi-VN-NamMinhNeural"),
  speed: z.number().positive().default(1.0),
  rate: z.string().default("+5%"),
  pitch: z.string().default("+0Hz"),
  volume: z.string().default("+0%"),
});

export const BeatRoleSchema = z.enum([
  "hook",
  "problem",
  "solution",
  "workflow",
  "benefits",
  "outro",
]);

export const VideoBeatSchema = z.object({
  id: z.string(),
  role: BeatRoleSchema,
  rawText: z.string(),
  normalizedVoiceText: z.string().optional(),
  voiceFile: z.string().optional(),
  durationSec: z.number().nonnegative().optional(),
  durationFrames: z.number().int().nonnegative().optional(),
  sfx: z.string().optional(),
  visual: z.record(z.any()).default({}),
});

export const VideoJobSchema = z.object({
  jobId: z.string(),
  title: z.string(),
  workshop: z.enum(["news", "explainer", "whiteboard"]),
  targetPlatform: z.enum(["tiktok", "youtube_shorts", "youtube_long"]).default("tiktok"),
  canvas: CanvasSchema.default({ width: 1080, height: 1920, fps: 30 }),
  voice: VoiceConfigSchema.default({}),
  beats: z.array(VideoBeatSchema).min(1),
  metadata: z.object({
    channel: z.string().default("Video Studio"),
    author: z.string().optional(),
    tags: z.array(z.string()).default([]),
    sourceUrl: z.string().optional(),
  }).default({}),
  output: z.object({
    dir: z.string().optional(),
    videoPath: z.string().optional(),
    captionPath: z.string().optional(),
  }).default({}),
});

export type VideoJob = z.infer<typeof VideoJobSchema>;
export type VideoBeat = z.infer<typeof VideoBeatSchema>;
export type BeatRole = z.infer<typeof BeatRoleSchema>;
