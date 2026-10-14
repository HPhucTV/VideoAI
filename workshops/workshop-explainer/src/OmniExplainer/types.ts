import { z } from "zod";

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
    left: z.object({ label: string(), value: string() }),
    right: z.object({ label: string(), value: string() }),
  }).optional(),
  cta: z.string().optional(),
});

function string() {
  return z.string();
}

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
