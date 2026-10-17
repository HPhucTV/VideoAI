import { describe, it, expect } from "vitest";
import { computeAudioHash, TTSRequest } from "../index.ts";

describe("TTS Cache Hash Key", () => {
  const baseReq: TTSRequest = {
    text: "Hôm nay trời đẹp",
    provider: "edge-tts",
    voice: "vi-VN-NamMinhNeural",
    rate: "+25%",
    pitch: "+0Hz",
    volume: "+0%",
  };

  it("thay đổi hash khi thay đổi pitch", () => {
    const hashNormal = computeAudioHash(baseReq, "Hôm nay trời đẹp");
    const reqDeep: TTSRequest = { ...baseReq, pitch: "-6Hz" };
    const hashDeep = computeAudioHash(reqDeep, "Hôm nay trời đẹp");

    expect(hashDeep).not.toBe(hashNormal);
  });

  it("thay đổi hash khi thay đổi volume", () => {
    const hashNormal = computeAudioHash(baseReq, "Hôm nay trời đẹp");
    const reqQuiet: TTSRequest = { ...baseReq, volume: "-20%" };
    const hashQuiet = computeAudioHash(reqQuiet, "Hôm nay trời đẹp");

    expect(hashQuiet).not.toBe(hashNormal);
  });
});
