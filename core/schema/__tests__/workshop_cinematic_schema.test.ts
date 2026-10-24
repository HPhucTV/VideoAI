import { describe, it, expect } from "vitest";
import { VideoJobSchema } from "../job.ts";
import { getArchetypeDefinition } from "../../beats/archetypes.ts";

describe("Job Schema Workshop Cinematic & Director Features Support", () => {
  it("chấp nhận workshop là 'cinematic' với archetype 'cinematic' và colorGradingPreset", () => {
    const jobData = {
      jobId: "test-cinematic-job",
      title: "Vạn Cổ Kiếm Tôn - Tập 1",
      workshop: "cinematic",
      archetype: "cinematic",
      canvas: {
        width: 1920,
        height: 1080,
        fps: 60,
        colorGradingPreset: "cinematic_teal_orange",
      },
      beats: [
        {
          id: "act1_b1",
          role: "act_1_establishment",
          speaker: "Diệp Thần",
          rawText: "Thiên Đạo bất công, ta liền nghịch thiên cải mệnh!",
          cues: {
            camera: "zoom_in_punch",
            sfx: "dramatic_boom",
            microStimulation: "zoom_punch",
          },
          visual: {
            prompt: "Ancient sword master standing in thunderstorm atop mountain peak",
            material: "donghua_3d",
          },
        },
        {
          id: "act5_b2",
          role: "act_5_resolution_loop",
          speaker: "Diệp Thần",
          rawText: "Kiếm ý bất diệt, vận mệnh luân hồi...",
          cues: {
            isLoopEnding: true,
            loopConnectingPhrase: "Bởi vì...",
          },
        },
      ],
    };

    const parsed = VideoJobSchema.parse(jobData);
    expect(parsed.workshop).toBe("cinematic");
    expect(parsed.archetype).toBe("cinematic");
    expect(parsed.canvas.colorGradingPreset).toBe("cinematic_teal_orange");
    expect(parsed.beats[0].cues?.microStimulation).toBe("zoom_punch");
    expect(parsed.beats[1].cues?.isLoopEnding).toBe(true);
  });

  it("getArchetypeDefinition('cinematic') trả về đủ 5 Hồi chuẩn điện ảnh", () => {
    const def = getArchetypeDefinition("cinematic");
    expect(def.id).toBe("cinematic");
    expect(def.beatRoles.length).toBe(5);
    expect(def.beatRoles[0].role).toBe("act_1_establishment");
    expect(def.beatRoles[4].role).toBe("act_5_resolution_loop");
  });
});
