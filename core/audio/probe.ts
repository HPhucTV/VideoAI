import { exec } from "node:child_process";
import { promisify } from "node:util";
import { readFile } from "node:fs/promises";

const execAsync = promisify(exec);

export interface AudioProbeResult {
  durationSec: number;
  durationFrames: number;
  source: "ffprobe" | "mp3-header";
}

/**
 * Đo thời lượng file audio bằng ffprobe (chuẩn xác micro-giây cho cả CBR và VBR).
 */
async function probeWithFfprobe(filePath: string): Promise<number | null> {
  try {
    const cmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${filePath}"`;
    const { stdout } = await execAsync(cmd);
    const parsed = parseFloat(stdout.trim());
    return isNaN(parsed) ? null : parsed;
  } catch {
    return null;
  }
}

/**
 * Thuật toán đọc MPEG Header dự phòng khi máy chưa có ffprobe (Fallback thuần TS).
 */
export function estimateMp3Duration(buffer: Buffer, defaultBitrateKbps = 48): number {
  if (!buffer || buffer.length === 0) return 0;
  let totalDuration = 0;
  let offset = 0;

  if (buffer.length > 10 && buffer.toString("utf8", 0, 3) === "ID3") {
    const id3Size =
      ((buffer[6] & 0x7f) << 21) |
      ((buffer[7] & 0x7f) << 14) |
      ((buffer[8] & 0x7f) << 7) |
      (buffer[9] & 0x7f);
    offset = 10 + id3Size;
  }

  const bitratesV2L3 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0];
  const sampleRatesV2 = [22050, 24000, 16000];

  while (offset < buffer.length - 4) {
    if (buffer[offset] === 0xff && (buffer[offset + 1] & 0xe0) === 0xe0) {
      const header = buffer.readUInt32BE(offset);
      const version = (header >> 19) & 3;
      const bitrateIdx = (header >> 12) & 15;
      const sampleRateIdx = (header >> 10) & 3;
      const padding = (header >> 9) & 1;

      let bitrate = 48;
      if (version === 3) {
        const bitratesV1L3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0];
        bitrate = bitratesV1L3[bitrateIdx] || defaultBitrateKbps;
      } else {
        bitrate = bitratesV2L3[bitrateIdx] || defaultBitrateKbps;
      }

      let sampleRate = 24000;
      if (sampleRateIdx < sampleRatesV2.length) {
        sampleRate = sampleRatesV2[sampleRateIdx];
      }

      const samplesPerFrame = version === 3 ? 1152 : 576;
      const frameLength = Math.floor((samplesPerFrame * (bitrate * 1000) / 8) / sampleRate) + padding;

      if (frameLength > 0 && offset + frameLength <= buffer.length) {
        totalDuration += samplesPerFrame / sampleRate;
        offset += frameLength;
        continue;
      }
    }
    offset++;
  }
  return totalDuration;
}

/**
 * Hàm đo thời lượng audio duy nhất của toàn hệ thống (30 FPS mặc định).
 */
export async function getAudioDuration(filePath: string, fps = 30): Promise<AudioProbeResult> {
  // 1. Thử ffprobe trước
  const ffprobeDuration = await probeWithFfprobe(filePath);
  if (ffprobeDuration !== null && ffprobeDuration > 0) {
    return {
      durationSec: ffprobeDuration,
      durationFrames: Math.ceil(ffprobeDuration * fps),
      source: "ffprobe",
    };
  }

  // 2. Fallback đọc MP3 Header
  const buf = await readFile(filePath);
  const headerDuration = estimateMp3Duration(buf);
  return {
    durationSec: headerDuration,
    durationFrames: Math.ceil(headerDuration * fps),
    source: "mp3-header",
  };
}
