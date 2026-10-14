import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { EdgeTTS } from "edge-tts-universal";
import { normalizeVietnameseText } from "../phonetics/rules.js";
import { getAudioDuration, type AudioProbeResult } from "../audio/probe.js";

export interface TTSRequest {
  text: string;
  provider?: "edge-tts" | "vbee" | "lucylab" | "elevenlabs";
  voice?: string;
  rate?: string;
  pitch?: string;
  volume?: string;
  speed?: number;
  fps?: number;
}

export interface TTSResponse {
  hash: string;
  filePath: string;
  normalizedText: string;
  cached: boolean;
  probe: AudioProbeResult;
}

const CACHE_DIR = join(process.cwd(), "core", "cache", "tts");

export function computeAudioHash(req: TTSRequest, normalizedText: string): string {
  const payload = `${req.provider || "edge-tts"}:${req.voice || "vi-VN-NamMinhNeural"}:${req.rate || "+5%"}:${normalizedText}`;
  return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}

export async function synthesizeVoice(req: TTSRequest): Promise<TTSResponse> {
  const provider = req.provider || "edge-tts";
  const voice = req.voice || "vi-VN-NamMinhNeural";
  const rate = req.rate || "+5%";
  const pitch = req.pitch || "+0Hz";
  const volume = req.volume || "+0%";
  const fps = req.fps || 30;

  // 1. Chuẩn hóa ngữ âm tiếng Việt
  const normalizedText = normalizeVietnameseText(req.text);

  // 2. Kiểm tra bộ nhớ đệm (Cache)
  await mkdir(CACHE_DIR, { recursive: true });
  const hash = computeAudioHash(req, normalizedText);
  const cachedFilePath = join(CACHE_DIR, `${hash}.mp3`);

  if (existsSync(cachedFilePath)) {
    const probe = await getAudioDuration(cachedFilePath, fps);
    return {
      hash,
      filePath: cachedFilePath,
      normalizedText,
      cached: true,
      probe,
    };
  }

  // 3. Tạo giọng đọc bằng Edge TTS
  if (provider === "edge-tts") {
    const tts = new EdgeTTS();
    const result = await tts.synthesize(normalizedText, voice, {
      rate,
      pitch,
      volume,
    });
    const buffer = await result.audio.toBuffer();
    await writeFile(cachedFilePath, buffer);
  } else {
    throw new Error(`TTS Provider "${provider}" requires external API credentials or is not yet configured.`);
  }

  const probe = await getAudioDuration(cachedFilePath, fps);
  return {
    hash,
    filePath: cachedFilePath,
    normalizedText,
    cached: false,
    probe,
  };
}
