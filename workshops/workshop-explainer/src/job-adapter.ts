import { readFile, writeFile, mkdir, copyFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { execFileSync } from "node:child_process";
import { VideoJobSchema, type VideoJob } from "../../../core/schema/job.ts";
import { synthesizeVoice } from "../../../core/tts/index.ts";
import type { OmniExplainerProps, OmniBeat } from "./OmniExplainer/types.ts";

export interface AdapterOptions {
  jobPath: string;
  outputDir?: string;
  synthesizeMissingAudio?: boolean;
}

export async function convertJobToRemotionProps(options: AdapterOptions): Promise<OmniExplainerProps> {
  const { jobPath, outputDir = join(process.cwd(), "output", "explainer"), synthesizeMissingAudio = true } = options;

  const raw = JSON.parse(await readFile(jobPath, "utf-8"));
  const job: VideoJob = VideoJobSchema.parse(raw);

  await mkdir(outputDir, { recursive: true });

  const publicAudioDir = join(process.cwd(), "workshops", "workshop-explainer", "public", "audio", job.jobId);
  await mkdir(publicAudioDir, { recursive: true });

  const isLandscape = job.targetPlatform === "youtube_long" || job.canvas.width > job.canvas.height;
  const fps = job.canvas.fps || 30;

  const beats: OmniBeat[] = [];

  for (let i = 0; i < job.beats.length; i++) {
    const beat = job.beats[i];
    let audioRelPath: string | undefined = undefined;
    let durationFrames = beat.durationFrames || 150;
    let voiceText = beat.rawText;

    if (synthesizeMissingAudio) {
      const voiceRes = await synthesizeVoice({
        text: beat.rawText,
        voice: beat.voice?.voiceId || job.voice.voiceId || "vi-VN-NamMinhNeural",
        rate: beat.voice?.rate || job.voice.rate || "+0%",
        pitch: beat.voice?.pitch || job.voice.pitch || "+0Hz",
        volume: beat.voice?.volume || job.voice.volume || "+0%",
        speed: beat.voice?.speed || job.voice.speed || 1.0,
        fps,
      });

      const audioDest = join(publicAudioDir, `${beat.id}.mp3`);
      await copyFile(voiceRes.filePath, audioDest);
      audioRelPath = `audio/${job.jobId}/${beat.id}.mp3`;
      durationFrames = voiceRes.probe.durationFrames;
      voiceText = voiceRes.normalizedText;
    }

    const visual = beat.visual || {};

    const omniBeat: OmniBeat = {
      id: beat.id,
      name: beat.role,
      voiceText,
      durationFrames,
      audioPath: audioRelPath,
      badge: beat.role.toUpperCase(),
      headline: visual.headline || visual.title || visual.statement || beat.role,
      subhead: visual.subhead || visual.context || visual.tag,
      highlightKeyword: visual.highlightKeyword || (beat.role === "hook" ? "Docker" : undefined),
      bullets: visual.bullets,
      stats: visual.value ? { value: String(visual.value), label: String(visual.label || "") } : undefined,
      comparison: visual.comparison,
      cta: visual.ctaTop || (beat.role === "outro" ? "THEO DÕI NGAY" : undefined),
      cues: beat.cues,
      speaker: beat.voice?.speaker,
    };

    beats.push(omniBeat);
  }

  const props: OmniExplainerProps = {
    jobId: job.jobId,
    title: job.title,
    subtitle: job.metadata?.channel || "OmniVideo Studio",
    channelName: job.metadata?.channel || "OMNIVIDEO STUDIO",
    orientation: isLandscape ? "landscape" : "portrait",
    beats,
  };

  const propsOut = join(outputDir, "props.json");
  await writeFile(propsOut, JSON.stringify(props, null, 2), "utf-8");

  // Also write to public/props.json so Remotion Studio picks it up by default
  const remotionPublicProps = join(process.cwd(), "workshops", "workshop-explainer", "public", "props.json");
  await writeFile(remotionPublicProps, JSON.stringify(props, null, 2), "utf-8");

  return props;
}

// CLI Execution Support
if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1"))) {
  const getArg = (flag: string) => {
    const idx = process.argv.indexOf(flag);
    return idx !== -1 && idx + 1 < process.argv.length ? process.argv[idx + 1] : null;
  };

  const jobArg = getArg("--job") || join(process.cwd(), "output", "sample_job.json");
  const renderArg = process.argv.includes("--render");

  try {
    const props = await convertJobToRemotionProps({ jobPath: jobArg });
    console.log(`Successfully converted ${jobArg} to Remotion props.`);
    console.log(`Total beats: ${props.beats.length}, Orientation: ${props.orientation}`);

    if (renderArg) {
      const compositionId = props.orientation === "landscape" ? "OmniExplainer-Landscape" : "OmniExplainer-Portrait";
      const outMp4 = join(process.cwd(), "output", "explainer", `${props.jobId}.mp4`);
      const propsPath = join(process.cwd(), "workshops", "workshop-explainer", "public", "props.json");

      console.log(`Rendering ${compositionId} to ${outMp4}...`);
      execFileSync(
        "npx.cmd",
        [
          "remotion",
          "render",
          compositionId,
          outMp4,
          `--props=${propsPath}`,
          "--gl=angle",
        ],
        {
          cwd: join(process.cwd(), "workshops", "workshop-explainer"),
          stdio: "inherit",
        }
      );
      console.log(`Render complete: ${outMp4}`);
    }
  } catch (err: any) {
    console.error("Adapter error:", err?.message || err);
    process.exit(1);
  }
}
