import "./index.css";
import React from "react";
import { Composition } from "remotion";
import { DockerExplainer } from "./DockerExplainer/DockerExplainer";
import { dockerExplainerSchema } from "./DockerExplainer/types";
import { OmniExplainer } from "./OmniExplainer/OmniExplainer";
import { omniExplainerSchema } from "./OmniExplainer/types";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1. Xưởng 2 Remotion: OmniExplainer Portrait (9:16 Shorts & TikTok) */}
      <Composition
        id="OmniExplainer-Portrait"
        component={OmniExplainer}
        durationInFrames={450}
        fps={90}
        width={1080}
        height={1920}
        schema={omniExplainerSchema}
        calculateMetadata={({ props }) => {
          const beats = props.beats || [];
          const totalFrames = beats.reduce((sum, b) => sum + (b.durationFrames || 450), 0);
          return {
            durationInFrames: Math.max(totalFrames, 450),
            props: {
              ...props,
              orientation: "portrait",
            },
          };
        }}
        defaultProps={{
          jobId: "sample-explainer-portrait",
          title: "OmniVideo Explainer (Portrait)",
          subtitle: "Dành cho TikTok & YouTube Shorts",
          channelName: "OMNIVIDEO STUDIO",
          orientation: "portrait",
          beats: [
            {
              id: "b1",
              name: "hook",
              voiceText: "Chào mừng bạn đến với OmniVideo Studio Local bản 2.0.",
              durationFrames: 450,
              badge: "CÔNG NGHỆ 2026",
              headline: "OmniVideo Studio Local",
              subhead: "Hệ thống video tự động 100% Offline",
              highlightKeyword: "OmniVideo",
            },
          ],
        }}
      />

      {/* 2. Xưởng 2 Remotion: OmniExplainer Landscape (16:9 YouTube Long-form) */}
      <Composition
        id="OmniExplainer-Landscape"
        component={OmniExplainer}
        durationInFrames={450}
        fps={90}
        width={1920}
        height={1080}
        schema={omniExplainerSchema}
        calculateMetadata={({ props }) => {
          const beats = props.beats || [];
          const totalFrames = beats.reduce((sum, b) => sum + (b.durationFrames || 450), 0);
          return {
            durationInFrames: Math.max(totalFrames, 450),
            props: {
              ...props,
              orientation: "landscape",
            },
          };
        }}
        defaultProps={{
          jobId: "sample-explainer-landscape",
          title: "OmniVideo Explainer (Landscape)",
          subtitle: "Dành cho YouTube Video Chuẩn 16:9",
          channelName: "OMNIVIDEO STUDIO",
          orientation: "landscape",
          beats: [
            {
              id: "b1",
              name: "hook",
              voiceText: "Chào mừng bạn đến với OmniVideo Studio Local bản 2.0.",
              durationFrames: 450,
              badge: "YOUTUBE LANDSCAPE",
              headline: "OmniVideo Studio Local",
              subhead: "Hệ thống video tự động 100% Offline",
              highlightKeyword: "OmniVideo",
            },
          ],
        }}
      />

      {/* 3. Original DockerExplainer Template (50s AI Voice Explainer) */}
      <Composition
        id="DockerExplainer"
        component={DockerExplainer}
        durationInFrames={3840}
        fps={90}
        width={1080}
        height={1920}
        schema={dockerExplainerSchema}
        defaultProps={{
          title: "Docker là gì?",
          subtitle: "Giải thích trong 50 giây",
        }}
      />
    </>
  );
};
