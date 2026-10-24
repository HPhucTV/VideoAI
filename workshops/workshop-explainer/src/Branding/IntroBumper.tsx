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

export interface IntroBumperProps {
  channelName?: string;
  tagline?: string;
  orientation?: "portrait" | "landscape";
}

export const IntroBumper: React.FC<IntroBumperProps> = ({
  channelName = "GIẢI MÃ TECH",
  tagline = "CÔNG NGHỆ · AI · LẬP TRÌNH",
  orientation = "landscape",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const isPortrait = orientation === "portrait";

  // 1. Spring-driven logo scale entrance
  const logoScale = spring({
    frame,
    fps,
    config: { damping: 11, stiffness: 140, mass: 0.7 },
  });

  // 2. Rotating cyber rings
  const ringRotate = (frame * 1.8) % 360;
  const ringScale = spring({
    frame: frame - 4,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  // 3. Shimmer light sweep across logo
  const shimmerX = interpolate(frame, [18, 55], [-120, 220], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 4. Headline text entrance
  const textY = spring({
    frame: frame - 10,
    fps,
    from: 50,
    to: 0,
    config: { damping: 13, stiffness: 120 },
  });
  const textOpacity = interpolate(frame, [10, 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 5. Tagline badge entrance
  const tagOpacity = interpolate(frame, [20, 36], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // 6. Outro quick fade out in last 10 frames for smooth transition
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{ opacity: fadeOut }}
      className="relative flex flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-slate-950 via-[#0a0f1d] to-black text-white select-none"
    >
      {/* Background Animated Neon Glows */}
      <div className="absolute h-[650px] w-[650px] rounded-full bg-cyan-500/20 blur-[130px]" />
      <div className="absolute h-[550px] w-[550px] rounded-full bg-purple-600/25 blur-[150px]" />

      {/* Background Cybernetic Radial Grid */}
      <div
        style={{
          transform: `scale(${ringScale}) rotate(${ringRotate}deg)`,
          opacity: 0.45,
        }}
        className="pointer-events-none absolute h-[700px] w-[700px] rounded-full border border-dashed border-cyan-400/40"
      />
      <div
        style={{
          transform: `scale(${ringScale}) rotate(${-ringRotate * 0.7}deg)`,
          opacity: 0.3,
        }}
        className="pointer-events-none absolute h-[850px] w-[850px] rounded-full border border-dotted border-purple-400/30"
      />

      {/* Main Container */}
      <div className="relative z-10 flex flex-col items-center justify-center gap-6">
        {/* Logo Container with Glow & Shimmer */}
        <div
          style={{ transform: `scale(${logoScale})` }}
          className="relative flex items-center justify-center"
        >
          {/* Outer Pulsing Glow */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-cyan-400 to-purple-600 blur-2xl opacity-60" />

          {/* Logo Frame */}
          <div className="relative h-44 w-44 overflow-hidden rounded-3xl border-2 border-cyan-400/50 bg-slate-900/90 p-4 shadow-[0_0_60px_rgba(6,182,212,0.6)] backdrop-blur-xl">
            <Img
              src={staticFile("giaimatech_logo.png")}
              className="h-full w-full object-contain drop-shadow-[0_0_20px_rgba(34,211,238,0.8)]"
            />
            {/* Shimmer Light Bar */}
            <div
              style={{
                transform: `translateX(${shimmerX}%) rotate(25deg)`,
              }}
              className="pointer-events-none absolute inset-0 -top-10 h-[200%] w-16 bg-gradient-to-r from-transparent via-white/50 to-transparent"
            />
          </div>
        </div>

        {/* Brand Headline */}
        <div
          style={{
            transform: `translateY(${textY}px)`,
            opacity: textOpacity,
          }}
          className="flex flex-col items-center text-center"
        >
          <h1
            className={`font-black tracking-wider uppercase drop-shadow-[0_4px_30px_rgba(0,0,0,0.9)] ${
              isPortrait ? "text-6xl" : "text-7xl"
            }`}
          >
            <span className="bg-gradient-to-r from-white via-cyan-200 to-sky-400 bg-clip-text text-transparent">
              {channelName}
            </span>
          </h1>

          {/* Subtitle Badge */}
          <div
            style={{ opacity: tagOpacity }}
            className="mt-4 flex items-center gap-3 rounded-full border border-purple-500/40 bg-purple-950/40 px-6 py-2 backdrop-blur-md"
          >
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xl font-bold tracking-widest text-purple-200 uppercase">
              {tagline}
            </span>
            <span className="h-2.5 w-2.5 rounded-full bg-purple-400 animate-pulse" />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
