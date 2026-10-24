import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface OutroBumperProps {
  channelName?: string;
  handle?: string;
  callToAction?: string;
  orientation?: "portrait" | "landscape";
}

export const OutroBumper: React.FC<OutroBumperProps> = ({
  channelName = "GIẢI MÃ TECH",
  handle = "@GiaiMaTech",
  callToAction = "ĐĂNG KÝ ĐỂ KHÔNG BỎ LỠ VIDEO MỚI",
  orientation = "landscape",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const isPortrait = orientation === "portrait";

  // 1. Card spring entrance
  const cardScale = spring({
    frame,
    fps,
    config: { damping: 13, stiffness: 120, mass: 0.8 },
  });

  // 2. Avatar rotating gradient ring
  const ringRotate = (frame * 2.2) % 360;

  // 3. Interactive Subscribe Button state
  // Click event triggers around frame 75
  const isClicked = frame >= 75;
  const clickScale = spring({
    frame: frame - 75,
    fps,
    from: 0.88,
    to: 1.0,
    config: { damping: 12, stiffness: 220 },
  });

  // Bell Jiggle / Shake at frame 85 and 180
  const bellShake1 =
    frame >= 85 && frame <= 115 ? Math.sin((frame - 85) * 0.8) * 18 : 0;
  const bellShake2 =
    frame >= 180 && frame <= 210 ? Math.sin((frame - 180) * 0.8) * 18 : 0;
  const bellRotation = bellShake1 + bellShake2;

  // 4. Smooth Fade Out in the last 15 frames
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{ opacity: fadeOut }}
      className="relative flex flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-black text-white select-none"
    >
      {/* Background Animated Atmosphere */}
      <div className="absolute -top-32 -left-32 h-[600px] w-[600px] rounded-full bg-cyan-600/15 blur-[150px]" />
      <div className="absolute -bottom-32 -right-32 h-[700px] w-[700px] rounded-full bg-purple-600/20 blur-[160px]" />
      <div className="absolute h-[450px] w-[450px] rounded-full bg-blue-600/10 blur-[130px]" />

      {/* Floating Glassmorphism Main Card */}
      <div
        style={{ transform: `scale(${cardScale})` }}
        className={`relative z-10 flex flex-col items-center justify-center rounded-3xl border border-cyan-400/30 bg-slate-900/80 p-12 shadow-[0_20px_80px_rgba(0,0,0,0.85)] backdrop-blur-2xl ${
          isPortrait ? "w-[880px] gap-8" : "w-[1080px] gap-8"
        }`}
      >
        {/* Avatar with Animated Conic Gradient Border */}
        <div className="relative flex items-center justify-center">
          <div
            style={{
              transform: `rotate(${ringRotate}deg)`,
              background:
                "conic-gradient(from 0deg, #06b6d4, #a855f7, #f59e0b, #06b6d4)",
            }}
            className="absolute h-36 w-36 rounded-full blur-md opacity-80"
          />
          <div className="relative h-32 w-32 overflow-hidden rounded-full border-2 border-slate-900 bg-slate-950 p-1">
            <Img
              src={staticFile("giaimatech_logo.png")}
              className="h-full w-full rounded-full object-cover"
            />
          </div>
        </div>

        {/* Channel Info */}
        <div className="flex flex-col items-center text-center">
          <div className="flex items-center gap-3">
            <h2 className="text-5xl font-black tracking-wide text-white drop-shadow-md uppercase">
              {channelName}
            </h2>
            {/* Verified Badge */}
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-cyan-500 text-sm font-bold text-slate-950 shadow-[0_0_15px_rgba(6,182,212,0.8)]">
              ✓
            </span>
          </div>
          <p className="mt-2 text-2xl font-semibold tracking-wider text-cyan-300">
            {handle}
          </p>
          <p className="mt-4 text-xl font-medium tracking-wide text-slate-300">
            {callToAction}
          </p>
        </div>

        {/* Dynamic Interactive Subscribe Button */}
        <div
          style={{ transform: `scale(${isClicked ? clickScale : 1.0})` }}
          className={`flex items-center justify-center gap-4 rounded-full px-12 py-5 font-black tracking-wider uppercase shadow-2xl transition-all duration-300 ${
            isClicked
              ? "border-2 border-cyan-400 bg-slate-950/90 text-cyan-300 shadow-[0_0_35px_rgba(6,182,212,0.6)]"
              : "bg-gradient-to-r from-red-600 via-rose-500 to-red-600 text-white shadow-[0_0_40px_rgba(225,29,72,0.7)]"
          }`}
        >
          {isClicked ? (
            <>
              <span className="text-3xl">ĐÃ ĐĂNG KÝ</span>
              <span
                style={{
                  transform: `rotate(${bellRotation}deg)`,
                  display: "inline-block",
                }}
                className="text-3xl"
              >
                🔔
              </span>
            </>
          ) : (
            <>
              <span className="h-4 w-4 rounded-full bg-white animate-ping" />
              <span className="text-3xl">ĐĂNG KÝ KÊNH</span>
              <span className="text-3xl">👆</span>
            </>
          )}
        </div>

        {/* Platform Pills */}
        <div className="flex items-center gap-4 text-sm font-bold tracking-wider text-slate-400 uppercase">
          <span className="rounded-lg bg-slate-800/80 px-4 py-2 text-red-400">
            ▶ YouTube
          </span>
          <span className="rounded-lg bg-slate-800/80 px-4 py-2 text-cyan-400">
            🎵 TikTok
          </span>
          <span className="rounded-lg bg-slate-800/80 px-4 py-2 text-blue-400">
            📘 Facebook
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
