import { z } from "zod";

export const CanvasSchema = z.object({
  width: z.number().int().positive().default(1080),
  height: z.number().int().positive().default(1920),
  fps: z.number().int().positive().default(60),
  colorGradingPreset: z.enum([
    "none",
    "cinematic_teal_orange",
    "donghua_xianxia_dream",
    "dark_thriller_noir",
    "vintage_warm"
  ]).default("none"),
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
  camera: z.enum([
    "zoom_in_punch", "zoom_out_slow", "shake_impact", "pan_left", "pan_right", "static",
    "orbit_360", "dolly_in", "dolly_out", "tilt_up", "tilt_down", "fpv"
  ]).optional(),
  sfx: z.string().optional(),
  hapticText: z.string().optional(),
  bRollKeyword: z.string().optional(),
  sticker: z.string().optional(),
  bgmDucking: z.enum(["none", "light", "heavy", "mute"]).optional(),
  isRehook: z.boolean().optional(),
  isLoopEnding: z.boolean().optional(),
  loopConnectingPhrase: z.string().optional(),
  microStimulation: z.enum(["zoom_punch", "sound_pop", "glitch_flash", "particle_burst"]).optional(),
});

export const VideoBeatSchema = z.object({
  id: z.string(),
  role: z.string(), // Hỗ trợ linh hoạt mọi Archetype
  rawText: z.string(),
  normalizedVoiceText: z.string().optional(),
  speaker: z.string().optional(),
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
  workshop: z.enum(["news", "explainer", "whiteboard", "blender", "cinematic"]),
  archetype: z.enum(["storytelling", "explainer", "versus", "mythbuster", "news", "cinematic"]).optional(),
  targetPlatform: z.enum(["tiktok", "youtube_shorts", "youtube_long", "youtube"]).default("tiktok"),
  canvas: CanvasSchema.default({ width: 1080, height: 1920, fps: 60 }),
  voice: VoiceConfigSchema.default({}),
  beats: z.array(VideoBeatSchema).min(1),
  metadata: z.object({
    channel: z.string().default("Video Studio"),
    author: z.string().optional(),
    tags: z.array(z.string()).default([]),
    sourceUrl: z.string().optional(),
    characters: z.array(z.string()).optional(),
    characters_voice: z.record(z.any()).optional(),
  }).passthrough().default({}),
  output: z.object({
    dir: z.string().optional(),
    videoPath: z.string().optional(),
    captionPath: z.string().optional(),
  }).default({}),
});

export type VideoJob = z.infer<typeof VideoJobSchema>;
export type VideoBeat = z.infer<typeof VideoBeatSchema>;
