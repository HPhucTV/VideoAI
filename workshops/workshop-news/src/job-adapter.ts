import type { VideoJob, VideoBeat } from "../../../core/schema/job.js";
import type { ScriptSchemaType, TemplateDataType } from "./render/script-schema.js";

/**
 * Ánh xạ VideoBeat từ hợp đồng job.json sang TemplateData tương ứng của HyperFrames
 */
export function mapBeatToTemplateData(beat: VideoBeat, job: VideoJob): TemplateDataType {
  const vis = beat.visual || {};

  switch (beat.role) {
    case "hook":
      return {
        template: "hook",
        headline: vis.headline || job.title.slice(0, 40),
        subhead: vis.subhead || (vis.tag ? String(vis.tag).slice(0, 40) : undefined),
        bgSrc: vis.bgSrc || "$source.image",
        kenBurns: vis.kenBurns || "zoom-in",
      };

    case "problem":
      if (vis.left && vis.right) {
        return {
          template: "comparison",
          left: vis.left,
          right: vis.right,
        };
      }
      return {
        template: "callout",
        statement: vis.statement || beat.rawText.slice(0, 80),
        tag: vis.tag || "Vấn đề",
      };

    case "solution":
    case "benefits":
      if (vis.value && vis.label) {
        return {
          template: "stat-hero",
          value: String(vis.value).slice(0, 20),
          label: String(vis.label).slice(0, 40),
          context: vis.context ? String(vis.context).slice(0, 50) : undefined,
        };
      }
      return {
        template: "callout",
        statement: vis.statement || beat.rawText.slice(0, 80),
        tag: vis.tag || (beat.role === "solution" ? "Giải pháp" : "Lợi ích"),
      };

    case "workflow":
      return {
        template: "feature-list",
        title: vis.title || "Quy trình thực hiện",
        bullets: vis.bullets || [beat.rawText.slice(0, 50)],
        icon: vis.icon,
      };

    case "outro":
    default:
      return {
        template: "outro",
        ctaTop: vis.ctaTop || "Theo dõi để xem thêm",
        channelName: vis.channelName || job.metadata?.channel || "Công nghệ 24h",
        source: vis.source || "OmniVideo Studio",
      };
  }
}

/**
 * Chuyển đổi toàn diện VideoJob thành ScriptSchema của Xưởng 1
 */
export function convertJobToNewsScript(job: VideoJob): ScriptSchemaType {
  return {
    version: "1.0",
    metadata: {
      title: job.title,
      source: {
        url: job.metadata?.sourceUrl || "https://local",
        domain: "local",
        image: job.beats.find((b) => b.visual?.bgSrc)?.visual?.bgSrc || null,
      },
      channel: job.metadata?.channel || "OmniVideo Studio",
    },
    voice: {
      provider: (job.voice?.provider as any) || "edge-tts",
      voiceId: job.voice?.voiceId || "vi-VN-NamMinhNeural",
      speed: job.voice?.speed || 1.0,
    },
    scenes: job.beats.map((beat) => ({
      id: beat.id,
      type: beat.role === "hook" ? "hook" : beat.role === "outro" ? "outro" : "body",
      voiceText: beat.normalizedVoiceText || beat.rawText,
      templateData: mapBeatToTemplateData(beat, job),
      sfx: beat.sfx ? { name: beat.sfx, volume: 0.4, startOffsetSec: 0 } : undefined,
    })),
  };
}
