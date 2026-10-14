#!/usr/bin/env node
import { normalizeVietnameseText } from "../phonetics/rules.ts";

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && idx + 1 < process.argv.length ? process.argv[idx + 1] : null;
}

const textArg = getArg("--text") || process.argv.slice(2).join(" ");

if (!textArg) {
  console.error("Usage: node --experimental-strip-types core/bin/phonetics.js --text \"văn bản cần đọc\"");
  process.exit(1);
}

const result = normalizeVietnameseText(textArg);
console.log(result);
