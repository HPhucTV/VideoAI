import { describe, it, expect } from "vitest";
import { VideoJobSchema, VideoBeatSchema } from "../job.ts";

describe("Job Schema Speaker Support", () => {
  it("chấp nhận trường speaker ở cấp root của beat", () => {
    const beatData = {
      id: "beat_01",
      role: "dialogue",
      speaker: "Lâm Mặc",
      rawText: "Các ngươi cứ đợi đấy!",
    };
    const parsed = VideoBeatSchema.parse(beatData);
    expect((parsed as any).speaker).toBe("Lâm Mặc");
  });

  it("giữ nguyên characters và characters_voice trong metadata", () => {
    const jobData = {
      jobId: "test-job",
      title: "Test",
      workshop: "whiteboard",
      beats: [{ id: "b1", role: "hook", rawText: "Xin chào" }],
      metadata: {
        channel: "Test Channel",
        characters: ["Lâm Mặc", "Triệu Vô Cực"],
        characters_voice: {
          "lâm mặc": { voice: "vi-VN-NamMinhNeural", rate: "+20%", pitch: "-3Hz" },
        },
      },
    };
    const parsed = VideoJobSchema.parse(jobData);
    expect((parsed.metadata as any).characters).toEqual(["Lâm Mặc", "Triệu Vô Cực"]);
    expect((parsed.metadata as any).characters_voice["lâm mặc"].pitch).toBe("-3Hz");
  });
});
