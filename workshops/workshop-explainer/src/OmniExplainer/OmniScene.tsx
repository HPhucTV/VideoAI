import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SubtitleBox } from "../DockerExplainer/components/SubtitleBox";
import type { OmniBeat } from "./types";

interface OmniSceneProps {
  beat: OmniBeat;
  channelName: string;
  orientation?: "portrait" | "landscape";
}

export const OmniScene: React.FC<OmniSceneProps> = ({
  beat,
  channelName,
  orientation = "portrait",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isPortrait = orientation === "portrait";

  // Spring animation for badge
  const badgeScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  // Spring animation for main content
  const contentY = spring({
    frame: frame - 5,
    fps,
    from: 50,
    to: 0,
    config: { damping: 14, stiffness: 90 },
  });

  const contentOpacity = interpolate(frame, [5, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill className={`flex flex-col items-center justify-between text-white select-none ${
      isPortrait ? "px-10 py-32" : "px-24 py-20"
    }`}>
      {/* Audio Layer */}
      {beat.audioPath && (
        <Audio src={staticFile(beat.audioPath)} />
      )}

      {/* Top Section: Badge */}
      <div
        style={{ transform: `scale(${badgeScale})` }}
        className="flex items-center gap-3 rounded-full border border-sky-400/40 bg-sky-500/10 px-8 py-3.5 backdrop-blur-md"
      >
        <span className="h-3.5 w-3.5 animate-ping rounded-full bg-sky-400" />
        <span className="text-2xl font-black tracking-widest text-sky-300 uppercase">
          {beat.badge || beat.name.toUpperCase()}
        </span>
      </div>

      {/* Center Section: Dynamic Visual Template */}
      <div
        style={{
          transform: `translateY(${contentY}px)`,
          opacity: contentOpacity,
        }}
        className="flex flex-1 flex-col items-center justify-center w-full max-w-4xl my-6"
      >
        {/* Template: Comparison */}
        {beat.comparison && (
          <div className={`grid w-full gap-6 ${isPortrait ? "grid-cols-1" : "grid-cols-2"}`}>
            <div className="rounded-3xl border border-rose-500/30 bg-rose-950/30 p-8 backdrop-blur-lg">
              <span className="text-xl font-bold text-rose-400 uppercase tracking-wider">
                {beat.comparison.left.label}
              </span>
              <p className="mt-3 text-3xl font-bold text-rose-100">
                {beat.comparison.left.value}
              </p>
            </div>
            <div className="rounded-3xl border border-emerald-500/30 bg-emerald-950/30 p-8 backdrop-blur-lg">
              <span className="text-xl font-bold text-emerald-400 uppercase tracking-wider">
                {beat.comparison.right.label}
              </span>
              <p className="mt-3 text-3xl font-bold text-emerald-100">
                {beat.comparison.right.value}
              </p>
            </div>
          </div>
        )}

        {/* Template: Stat Hero */}
        {beat.stats && (
          <div className="flex flex-col items-center justify-center rounded-3xl border border-cyan-400/40 bg-slate-900/80 px-16 py-12 text-center shadow-[0_0_80px_rgba(34,211,238,0.2)] backdrop-blur-xl">
            <span className="text-7xl font-black tracking-tight text-cyan-300 drop-shadow-[0_0_30px_rgba(34,211,238,0.6)]">
              {beat.stats.value}
            </span>
            <span className="mt-4 text-2xl font-semibold text-slate-200">
              {beat.stats.label}
            </span>
          </div>
        )}

        {/* Template: Feature List / Bullets */}
        {beat.bullets && beat.bullets.length > 0 && (
          <div className="flex flex-col gap-4 w-full max-w-2xl">
            {beat.headline && (
              <h2 className="text-3xl font-black text-center text-sky-200 mb-2">
                {beat.headline}
              </h2>
            )}
            {beat.bullets.map((bullet, i) => (
              <div
                key={i}
                className="flex items-center gap-4 rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5 backdrop-blur-md"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sky-500/20 text-xl font-bold text-sky-400">
                  {i + 1}
                </span>
                <span className="text-2xl font-bold text-slate-100">{bullet}</span>
              </div>
            ))}
          </div>
        )}

        {/* Template: Outro / CTA */}
        {beat.cta && (
          <div className="flex flex-col items-center justify-center text-center">
            <div className="rounded-full border border-sky-400/60 bg-gradient-to-r from-sky-500 to-indigo-600 px-12 py-5 shadow-[0_0_50px_rgba(56,189,248,0.4)]">
              <span className="text-3xl font-black tracking-wide text-white uppercase">
                {beat.cta}
              </span>
            </div>
            <p className="mt-8 text-2xl font-semibold text-slate-300">
              Kênh chính thức: <span className="text-sky-300 font-bold">{channelName}</span>
            </p>
          </div>
        )}

        {/* Default / Hook Headline */}
        {!beat.comparison && !beat.stats && (!beat.bullets || beat.bullets.length === 0) && !beat.cta && (
          <div className="text-center">
            {beat.headline && (
              <h1 className="text-5xl font-black leading-tight tracking-tight text-white drop-shadow-[0_4px_20px_rgba(0,0,0,0.8)]">
                {beat.headline}
              </h1>
            )}
            {beat.subhead && (
              <p className="mt-6 text-3xl font-semibold text-sky-300">
                {beat.subhead}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Bottom Section: Synchronized Subtitle Box */}
      <div className="w-full flex justify-center">
        <SubtitleBox
          text={beat.voiceText}
          durationInFrames={beat.durationFrames}
          highlightKeyword={beat.highlightKeyword}
          className="mt-0"
        />
      </div>
    </AbsoluteFill>
  );
};
