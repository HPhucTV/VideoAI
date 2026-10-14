import { z } from "zod";

export const visualCueSchema = z.object({
  camera: z.string().optional(),
  sfx: z.string().optional(),
  hapticText: z.string().optional(),
  sticker: z.string().optional(),
  isRehook: z.boolean().optional(),
  bgmDucking: z.string().optional(),
});

export const omniBeatSchema = z.object({
  id: z.string(),
  name: z.string().default("beat"),
  voiceText: z.string(),
  durationFrames: z.number().default(150),
  audioPath: z.string().optional(),
  badge: z.string().optional(),
  headline: z.string().optional(),
  subhead: z.string().optional(),
  highlightKeyword: z.string().optional(),
  bullets: z.array(z.string()).optional(),
  stats: z.object({
    value: z.string(),
    label: z.string(),
  }).optional(),
  comparison: z.object({
    left: z.object({ label: z.string(), value: z.string() }),
    right: z.object({ label: z.string(), value: z.string() }),
  }).optional(),
  cta: z.string().optional(),
  cues: visualCueSchema.optional(),
  speaker: z.string().optional(),
});

export const omniExplainerSchema = z.object({
  jobId: z.string().default("omni-sample"),
  title: z.string().default("OmniVideo Explainer"),
  subtitle: z.string().default("Giải thích bằng Video-as-Code"),
  channelName: z.string().default("OMNIVIDEO STUDIO"),
  orientation: z.enum(["portrait", "landscape"]).default("portrait"),
  beats: z.array(omniBeatSchema).default([]),
});

export type OmniBeat = z.infer<typeof omniBeatSchema>;
export type OmniExplainerProps = z.infer<typeof omniExplainerSchema>;
