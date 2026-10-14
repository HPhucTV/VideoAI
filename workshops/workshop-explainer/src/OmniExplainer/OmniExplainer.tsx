import React from "react";
import {
  AbsoluteFill,
  Series,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BrandHeader } from "../DockerExplainer/components/BrandHeader";
import { OmniScene } from "./OmniScene";
import type { OmniExplainerProps } from "./types";

export const OmniExplainer: React.FC<OmniExplainerProps> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const beats = props.beats && props.beats.length > 0 ? props.beats : [
    {
      id: "sample_hook",
      name: "hook",
      voiceText: "Chào mừng bạn đến với OmniVideo Studio Local bản 2.0.",
      durationFrames: 150,
      badge: "CÔNG NGHỆ 2026",
      headline: "OmniVideo Studio Local",
      subhead: "Hệ thống video tự động 100% Offline",
      highlightKeyword: "OmniVideo",
    },
  ];

  // Gentle fade in at start and fade out at end
  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );
  const opacity = fadeIn * fadeOut;

  return (
    <AbsoluteFill
      style={{ opacity }}
      className="relative overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-black font-sans text-white select-none"
    >
      {/* Brand Header */}
      <BrandHeader channelName={props.channelName || "OMNIVIDEO STUDIO"} />

      {/* Background Animated Subtle Glows */}
      <div className="absolute -top-40 -left-40 h-[600px] w-[600px] rounded-full bg-sky-600/15 blur-[140px]" />
      <div className="absolute top-1/2 -right-40 h-[700px] w-[700px] rounded-full bg-indigo-600/15 blur-[160px]" />
      <div className="absolute -bottom-40 left-1/4 h-[600px] w-[600px] rounded-full bg-blue-600/15 blur-[140px]" />

      {/* Dynamic Sequence of Beats */}
      <Series>
        {beats.map((beat) => (
          <Series.Sequence
            key={beat.id}
            durationInFrames={beat.durationFrames}
          >
            <OmniScene
              beat={beat}
              channelName={props.channelName || "OMNIVIDEO STUDIO"}
              orientation={props.orientation}
            />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
