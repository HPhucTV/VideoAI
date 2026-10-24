/**
 * OmniVideo Studio - Beat Engineering Schema v2.1
 * Single Source of Truth for Scriptwriting, Retention, and Multi-Voice Beats.
 */

export type BeatArchetype = 
  | "storytelling"   // Cổ tích / Drama / Narrative (Dan Harmon Story Circle)
  | "explainer"      // Kỹ thuật / Kiến thức (PAS: Problem - Agitate - Solve)
  | "versus"         // So sánh đối đầu A vs B
  | "mythbuster"     // Lật tẩy lầm tưởng / Phá bỏ định kiến
  | "news"           // Tin tức / Thời sự công nghệ (Inverted Pyramid)
  | "cinematic";     // Phim Điện Ảnh 3D & Donghua (5-Act Dramatic Structure)

export interface VisualCue {
  /** Hiệu ứng camera: zoom đột ngột, lia ngang, rung nhẹ */
  camera?: "zoom_in_punch" | "zoom_out_slow" | "shake_impact" | "pan_left" | "pan_right" | "static";
  /** Hiệu ứng âm thanh SFX đồng bộ khi bắt đầu beat */
  sfx?: "whoosh_impact" | "pop_bubble" | "ding_idea" | "glitch_error" | "dramatic_boom" | "cash_register" | "cheer_success";
  /** Từ khóa nhấn mạnh thị giác (chữ phóng to, nhấp nháy, đổi màu) */
  hapticText?: string;
  /** Từ khóa để AI tìm hoặc vẽ B-Roll / hình ảnh minh họa */
  bRollKeyword?: string;
  /** Sticker cảm xúc hoặc meme minh họa */
  sticker?: "shocked" | "thinking" | "fire" | "warning" | "verified" | "laugh";
  /** Mức độ hạ nhạc nền để tôn giọng nói kịch tính */
  bgmDucking?: "none" | "light" | "heavy" | "mute";
  /** Đánh dấu nhịp này là điểm tái kích thích giữ chân khán giả (giây thứ 20-30) */
  isRehook?: boolean;
  /** Đánh dấu nhịp này là vòng lặp kết nối liền mạch với câu mở đầu (The Infinite Loop) */
  isLoopEnding?: boolean;
  /** Cụm từ bắc cầu vòng lặp về câu mở đầu */
  loopConnectingPhrase?: string;
  /** Kích thích vi mô mỗi 3.5 giây để giữ sự tỉnh táo của não bộ */
  microStimulation?: "zoom_punch" | "sound_pop" | "glitch_flash" | "particle_burst";
}

export interface BeatVoiceOverride {
  /** Mã giọng đọc Edge TTS (vi-VN-NamMinhNeural, vi-VN-HoaiMyNeural, v.v.) */
  voiceId?: string;
  /** Tốc độ đọc: "+0%", "+5%", "+10%", "-5%" */
  rate?: string;
  /** Độ cao giọng: "+0Hz", "+2Hz", "-5Hz" */
  pitch?: string;
  /** Âm lượng */
  volume?: string;
  /** Tốc độ số thực: 1.0, 1.15 */
  speed?: number;
  /** Khoảng lặng nghỉ sau khi đọc hết câu (mili-giây) */
  pauseAfterMs?: number;
  /** Tên nhân vật đảm nhận lời thoại này (nếu là kịch bản đối thoại) */
  speaker?: string;
}

export interface UnifiedBeatV2 {
  /** Mã định danh duy nhất của beat: beat_01, beat_02... */
  id: string;
  /** Vai trò tự sự theo từng Archetype */
  role: string;
  /** Lời thoại nguyên bản của beat */
  rawText: string;
  /** Cấu hình giọng đọc và nhịp độ riêng cho beat (ghi đè voice cấp Job) */
  voice?: BeatVoiceOverride;
  /** Các chỉ định nghe-nhìn, camera, SFX tạo cảm xúc */
  cues?: VisualCue;
  /** Dữ liệu hiển thị UI đặc thù của từng Xưởng */
  visual?: {
    headline?: string;
    subhead?: string;
    highlightKeyword?: string;
    bullets?: string[];
    value?: string;
    label?: string;
    region?: { x: number; y: number; width: number; height: number };
    [key: string]: any;
  };
  /** Đánh dấu nhịp này là vòng lặp kết nối liền mạch với câu mở đầu */
  isLoopEnding?: boolean;
  /** Cụm từ nối vòng lặp */
  loopConnectingPhrase?: string;
  /** Thời lượng tính bằng giây sau khi tổng hợp TTS & ffprobe */
  durationSec?: number;
  /** Thời điểm bắt đầu tính bằng giây trong timeline video */
  startSec?: number;
}

export interface ArchetypeDefinition {
  id: BeatArchetype;
  name: string;
  description: string;
  targetPlatform: "tiktok" | "youtube" | "both";
  recommendedDurationSec: { min: number; ideal: number; max: number };
  beatRoles: Array<{
    role: string;
    name: string;
    purpose: string;
    idealPercent: string;
    defaultVoiceTone?: string;
    retentionTip?: string;
  }>;
}
