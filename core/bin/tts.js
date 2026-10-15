#!/usr/bin/env node
import { synthesizeVoice } from "../tts/index.ts";

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && idx + 1 < process.argv.length ? process.argv[idx + 1] : null;
}

const textArg = getArg("--text");
const voiceArg = getArg("--voice") || "vi-VN-NamMinhNeural";
const rateArg = getArg("--rate") || "+0%";
const pitchArg = getArg("--pitch") || "+0Hz";
const volumeArg = getArg("--volume") || "+0%";
const fpsArg = parseInt(getArg("--fps") || "60", 10);

if (!textArg) {
  console.error(JSON.stringify({ error: "Missing --text argument" }));
  process.exit(1);
}

try {
  const result = await synthesizeVoice({
    text: textArg,
    voice: voiceArg,
    rate: rateArg,
    pitch: pitchArg,
    volume: volumeArg,
    fps: fpsArg,
  });
  console.log(JSON.stringify(result));
} catch (err) {
  console.error(JSON.stringify({ error: String(err?.message || err) }));
  process.exit(1);
}
