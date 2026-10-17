import { describe, it, expect } from "vitest";
import { VideoJobSchema } from "../job.ts";

describe("Job Schema Workshop Blender Support", () => {
  it("chấp nhận workshop là 'blender'", () => {
    const jobData = {
      jobId: "test-blender-job",
      title: "Test 3D Animation",
      workshop: "blender",
      archetype: "storytelling",
      beats: [
        {
          id: "b1",
          role: "hook",
          speaker: "Lâm Mặc",
          rawText: "Vạn kiếm quy tông!",
          cues: { camera: "zoom_in_punch" },
        },
      ],
    };

    const parsed = VideoJobSchema.parse(jobData);
    expect(parsed.workshop).toBe("blender");
  });
});
