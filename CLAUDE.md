# OMNIVIDEO STUDIO — CODEX & CLAUDE CODE INSTRUCTIONS

See [AGENTS.md](file:///c:/Users/tranh/Documents/Duy/VideoAI/AGENTS.md) and [docs/CINEMATIC_STANDARDS.md](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/CINEMATIC_STANDARDS.md) for full production rules.

## Core Rules For Film Production (Workshop 4 - Cinematic)
1. **Average Shot Length (ASL):** 4.0s - 7.0s per shot.
2. **Shot Count Requirement:**
   - 1 min = 10-14 shots
   - 3 min = 25-35 shots
   - **5 min = 45-60 shots**
   - 10 min = 90-120 shots
3. **MANDATORY GEN V AI VIDEO GENERATION (NO ZOOMPAN ON STILL IMAGES):** Every single shot MUST be generated as real moving AI video (`GEN V`) using Google Flow (Veo 2 or Omni Flash) via `/api/flow/generate-video`. NEVER replace AI video with static image zoompan / Ken Burns slideshows. Still images (`GEN I`) are only used as start-frames.
4. **ZERO-LOOP MANDATE:** NEVER loop Veo 2 / AI clips using `-stream_loop`. Always cut into multiple camera angles (Shot/Reverse-Shot: Establishing -> Speaker -> Reaction -> Over-the-shoulder -> Insert detail).
5. **Native Vietnamese Voice Engine:** Microsoft Edge-TTS Vietnamese Neural with 48,000 Hz Stereo 192k AAC. Modulate pitch and rate per character so voices are distinct and lifelike. BGM ducking at -18dB.
6. **Auto-Beat 5-Act Screenplay & Golden Dialogue Rule:** 5 Acts (15%, 25%, 30%, 20%, 10%). Every line of dialogue MUST be <= 20 Vietnamese words (4.0s - 6.5s audio). Auto-break long speeches across alternating camera angles.
7. **Locked Art Style Presets:** Choose exactly ONE preset per project (`PRESET_DONGHUA_3D` 1:7, `PRESET_CHIBI_3D` 1:3, or `PRESET_ANIME_25D`). Never mix Chibi with realistic proportions.
8. **Virtual Sets & Zero Drift:** Cap at 2-3 master locations per episode. Generate 4K Master Environment Plates via Google Flow. Camera must only navigate within locked sets; never hallucinate unscripted random buildings or rooms.
9. **Cinematic Prompt Transformer:** Automatically translate violent/intense script actions (slap, strike, blood, kill) into dynamic physical energy, atmospheric wind, lighting, and solemn gestures so Google Flow safety filters never silently reject prompts.
10. **The 7-Gate Production Protocol (Mandatory User Approval Gates):**
    - Gate 1: Concept & Genre (AI proposes 3 ideas -> User selects)
    - Gate 2: 5-Act Screenplay & Dialogue (45-60 short beats <= 20 words, Voice x1.25)
    - Gate 3: Google Flow Asset Approval (Character Anchors & 2-3 Master Environment Plates -> User approves, Fresh-Render)
    - Gate 4: Audio Voice Master (48kHz Edge-TTS + Character Modulations, Voice x1.25)
    - Gate 5: Storyboard Keyframe Consistency (Inherit locked Media IDs)
    - Gate 6: 100% GEN V AI Video Generation & FFmpeg Master Assembly (Thematic Chatbox + 3D Thumbnail)
    - Gate 7: YouTube Unlisted Publishing (Automatic Publishing Kit, SEO Title/Tags, Chapters, Vietnamese SRT, Thumbnail Upload, Unlisted Mode Default)
11. **Gate 7 YouTube Unlisted Privacy Mandate:** Automatically package Publishing Kit (Title, Chapters, Tags), upload master MP4, set SRT subtitles, attach High-CTR 3D Thumbnail, and ALWAYS default to `unlisted` privacy.
12. **Fresh-Render Mandate (Zero Asset Reuse):** Every new episode/job must render 100% fresh assets (images at Gate 3/5, video at Gate 6). Strictly forbid copying or reusing stale clips/images from previous jobs. Isolate output folders per `job_id`.

## Core Rules For Threads Video Production (Workshop 5 - Threads & Social Drama)
1. **Dark Mode AMOLED (#101010) & Pixel-Perfect Dimensions:** Default to `#101010` dark theme, `1px solid #282828` border, `18px` border-radius, width `820px`, padding `22px 24px`. NEVER use plain white cartoonish bubbly cards.
2. **Real Avatars & Media (Method A2):** Always cache and display 100% real photographic avatars from Instagram CDN for the post author and all commenters. NEVER fall back to letter initial circles. Preserve post media aspect ratio in `14px` rounded containers.
3. **Audio Purifier & Slang Normalizer:** Strip 100% ASCII emoticons (`=)))`, `:)))`, `^^`, `-))`, etc.) and emojis before Edge-TTS. Transliterate English loanwords (`teamwork` -> `tim quớc`, `deadline` -> `đét lai`, `tsv` -> `tân sinh viên`, `dh` -> `đại học`, `clm` -> `vãi chưởng`, `t` -> `tao`, `m` -> `mày`, `đc` -> `được`). Add `0.35s tail padding` to prevent syllable clipping.
4. **Concentric Channel Brand Watermark:** Circular channel avatar at `y ≈ 130px` must be mathematically centered with an alpha circular mask (0.0px offset), accompanied by bold `HANSHIN THREADS` title.
5. **Nested Thread View & Zero Karaoke Clutter:** Always display parent context snippet with gray vertical connector line. Remove distracting bottom karaoke boxes.
6. **Audio-Visual Punchline Comedy Sync:** Card entry at `t = 0.0s` only plays subtle `pop.wav` (vol 0.60). Comedic Meme SFX (`vine_boom.wav`, `bruh.wav`, `quack.wav`, etc.) hits at the **punchline moment** synchronized with a die-cut **Meme Sticker (PNG in `assets/memes/`) popping up via spring bounce** in the lower third area.
7. **Dynamic BGM Ducking:** Base volume `0.35 - 0.40` ducked automatically during speech via sidechain compression, swelling during awkward silences and punchlines.

## Quick CLI Execution
- Run unified studio pipeline (Gates 3 -> 7):
  ```bash
  python scripts/studio_pipeline.py --job <job_id> --publish-youtube
  ```
- Run Workshop 5 Threads production:
  ```bash
  python scripts/produce_njskmel_thread.py
  ```
