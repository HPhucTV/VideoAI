import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { writeFile, mkdir } from "node:fs/promises";
import { join, dirname } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { normalizeVietnameseText } from "../phonetics/rules.ts";
import { getAudioDuration, type AudioProbeResult } from "../audio/probe.ts";

const execFileAsync = promisify(execFile);

export interface TTSRequest {
  text: string;
  provider?: "edge-tts" | "vbee" | "lucylab" | "elevenlabs";
  voice?: string;
  rate?: string;
  pitch?: string;
  volume?: string;
  speed?: number;
  fps?: number;
  srtPath?: string;
}

export interface TTSResponse {
  hash: string;
  filePath: string;
  normalizedText: string;
  cached: boolean;
  probe: AudioProbeResult;
  srtPath?: string;
}

import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = join(__dirname, "..", "..");
const CACHE_DIR = join(ROOT_DIR, "core", "cache", "tts");

function findPythonExe(): string {
  const venvPy = join(ROOT_DIR, "workshops", "workshop-whiteboard", ".venv", "Scripts", "python.exe");
  if (existsSync(venvPy)) return venvPy;
  return "python";
}

export function computeAudioHash(req: TTSRequest, normalizedText: string): string {
  const payload = `${req.provider || "edge-tts"}:${req.voice || "vi-VN-NamMinhNeural"}:${req.rate || "+0%"}:${normalizedText}`;
  return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}

export async function synthesizeVoice(req: TTSRequest): Promise<TTSResponse> {
  const provider = req.provider || "edge-tts";
  const voice = req.voice || "vi-VN-NamMinhNeural";
  const rate = req.rate || "+0%";
  const pitch = req.pitch || "+0Hz";
  const volume = req.volume || "+0%";
  const fps = req.fps || 30;

  // 1. Chuẩn hóa ngữ âm tiếng Việt bằng Single Source of Truth
  const normalizedText = normalizeVietnameseText(req.text);

  // 2. Kiểm tra bộ nhớ đệm (Cache)
  await mkdir(CACHE_DIR, { recursive: true });
  const hash = computeAudioHash(req, normalizedText);
  const cachedFilePath = join(CACHE_DIR, `${hash}.mp3`);
  const cachedSrtPath = join(CACHE_DIR, `${hash}.vtt`);

  if (existsSync(cachedFilePath)) {
    const probe = await getAudioDuration(cachedFilePath, fps);
    return {
      hash,
      filePath: cachedFilePath,
      normalizedText,
      cached: true,
      probe,
      srtPath: existsSync(cachedSrtPath) ? cachedSrtPath : undefined,
    };
  }

  // 3. Tạo giọng đọc bằng Edge TTS via reliable local engine
  if (provider === "edge-tts") {
    const pythonExe = findPythonExe();
    const args = [
      "-m", "edge_tts",
      "--text", normalizedText,
      "--voice", voice,
      "--write-media", cachedFilePath,
      "--write-subtitles", cachedSrtPath,
    ];
    if (rate && rate !== "+0%") {
      args.push(`--rate=${rate}`);
    }
    if (pitch && pitch !== "+0Hz") {
      args.push(`--pitch=${pitch}`);
    }
    if (volume && volume !== "+0%") {
      args.push(`--volume=${volume}`);
    }

    try {
      await execFileAsync(pythonExe, args);
    } catch (err: any) {
      throw new Error(`Edge TTS generation failed: ${err?.stderr || err?.message || err}`);
    }
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
    srtPath: existsSync(cachedSrtPath) ? cachedSrtPath : undefined,
  };
}
