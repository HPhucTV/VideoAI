import { z } from "zod";

export const CanvasSchema = z.object({
  width: z.number().int().positive().default(1080),
  height: z.number().int().positive().default(1920),
  fps: z.number().int().positive().default(60),
});

export const VoiceConfigSchema = z.object({
  provider: z.enum(["edge-tts", "vbee", "lucylab", "elevenlabs"]).default("edge-tts"),
  voiceId: z.string().default("vi-VN-NamMinhNeural"),
  speed: z.number().positive().default(1.0),
  rate: z.string().default("+0%"),
  pitch: z.string().default("+0Hz"),
  volume: z.string().default("+0%"),
});

export const BeatVoiceSchema = z.object({
  voiceId: z.string().optional(),
  speed: z.number().positive().optional(),
  rate: z.string().optional(),
  pitch: z.string().optional(),
  volume: z.string().optional(),
  pauseAfterMs: z.number().nonnegative().optional(),
  speaker: z.string().optional(),
});

export const VisualCueSchema = z.object({
  camera: z.enum(["zoom_in_punch", "zoom_out_slow", "shake_impact", "pan_left", "pan_right", "static"]).optional(),
  sfx: z.string().optional(),
  hapticText: z.string().optional(),
  bRollKeyword: z.string().optional(),
  sticker: z.string().optional(),
  bgmDucking: z.enum(["none", "light", "heavy", "mute"]).optional(),
  isRehook: z.boolean().optional(),
});

export const VideoBeatSchema = z.object({
  id: z.string(),
  role: z.string(), // Hỗ trợ linh hoạt mọi Archetype
  rawText: z.string(),
  normalizedVoiceText: z.string().optional(),
  voice: BeatVoiceSchema.optional(), // Đa giọng đọc / pacing theo từng beat
  cues: VisualCueSchema.optional(),  // Retention cues, SFX, Camera
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
  archetype: z.enum(["storytelling", "explainer", "versus", "mythbuster", "news"]).optional(),
  targetPlatform: z.enum(["tiktok", "youtube_shorts", "youtube_long", "youtube"]).default("tiktok"),
  canvas: CanvasSchema.default({ width: 1080, height: 1920, fps: 60 }),
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
