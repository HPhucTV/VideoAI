#!/usr/bin/env node
import { getAudioDuration } from "../audio/probe.js";

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && idx + 1 < process.argv.length ? process.argv[idx + 1] : null;
}

const file = getArg("--file") || process.argv[2];
const fps = parseInt(getArg("--fps") || "30", 10);

if (!file) {
  console.error(JSON.stringify({ error: "Missing --file argument" }));
  process.exit(1);
}

try {
  const result = await getAudioDuration(file, fps);
  console.log(JSON.stringify(result));
} catch (err) {
  console.error(JSON.stringify({ error: String(err) }));
  process.exit(1);
}
