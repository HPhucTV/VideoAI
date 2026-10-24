/**
 * OMNIVIDEO STUDIO - ANTIGRAVITY 2.0 LIVE BRIDGE
 * Module kết nối trực tiếp hai chiều giữa Web Dashboard và IDE Google Antigravity 2.0:
 * 1. Tự động phát hiện phiên Antigravity đang chạy (Active Conversation Discovery).
 * 2. Theo dõi thời gian thực luồng suy nghĩ (Thinking), Công cụ thực thi (Tool Calls), và Trạng thái 7 Cổng (Real-time SSE Stream).
 * 3. Bắn lệnh sản xuất & Phê duyệt kịch bản/Asset trực tiếp từ Web sang IDE (AgentAPI IPC Dispatcher).
 */

import { existsSync, readdirSync, statSync, readFileSync, watch } from "node:fs";
import type { FSWatcher } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
import { spawn } from "node:child_process";

const HOME = homedir();
const AGY_DIR = join(HOME, ".gemini", "antigravity");
const PRESENCE_DIR = join(AGY_DIR, "presence");
const BRAIN_DIR = join(AGY_DIR, "brain");
const AGENTAPI_BAT = join(AGY_DIR, "bin", "agentapi.bat");

export interface AntigravitySession {
  conversationId: string;
  isActive: boolean;
  transcriptPath: string;
  transcriptSize: number;
  lastModified: string;
}

export interface TranscriptEvent {
  stepIndex: number;
  type: string;
  status: string;
  timestamp: string;
  thought?: string;
  tools?: string[];
  toolDetails?: Array<{ name: string; summary?: string; command?: string }>;
  gate?: {
    gateNumber: number;
    gateName: string;
    progressPercent: number;
  };
  contentPreview?: string;
}

/**
 * Tự động tìm kiếm Conversation ID đang hoạt động gần nhất của Antigravity 2.0
 */
export function getActiveConversationId(): string | null {
  if (!existsSync(PRESENCE_DIR)) return null;
  try {
    const locks = readdirSync(PRESENCE_DIR)
      .filter(f => f.endsWith(".lock"))
      .map(f => {
        const full = join(PRESENCE_DIR, f);
        return {
          id: f.replace(".lock", ""),
          mtime: statSync(full).mtimeMs,
        };
      })
      .sort((a, b) => b.mtime - a.mtime);

    return locks.length > 0 ? locks[0].id : null;
  } catch (err) {
    console.error("[AntigravityBridge] Lỗi đọc presence directory:", err);
    return null;
  }
}

/**
 * Lấy thông tin trạng thái chi tiết của phiên Antigravity
 */
export function getAntigravitySession(convoId?: string): AntigravitySession | null {
  const targetId = convoId || getActiveConversationId();
  if (!targetId) return null;

  const tPath = join(BRAIN_DIR, targetId, ".system_generated", "logs", "transcript.jsonl");
  const exists = existsSync(tPath);
  const size = exists ? statSync(tPath).size : 0;
  const mtime = exists ? statSync(tPath).mtime.toISOString() : new Date().toISOString();

  return {
    conversationId: targetId,
    isActive: true,
    transcriptPath: tPath,
    transcriptSize: size,
    lastModified: mtime,
  };
}

export interface ProductionStudioState {
  currentGate: number;
  gateName: string;
  progressPercent: number;
  isCompleted: boolean;
  completedGates: number[];
  activeJobId?: string;
  masterVideoPath?: string;
  lastUpdated: string;
}

/**
 * Suy luận Cổng sản xuất (Gate 1 -> Gate 7) từ nội dung của bước thực thi
 * Chỉ trả về Gate khi có bằng chứng thực tế, trả về null nếu là bước phụ (git, file check, generic output)
 */
export function inferProductionGate(stepObj: any): {
  gateNumber: number;
  gateName: string;
  progressPercent: number;
  isCompleted?: boolean;
} | null {
  const content = (stepObj.content || "").toLowerCase();
  const thinking = (stepObj.thinking || "").toLowerCase();
  const text = `${content} ${thinking}`;

  // Kiểm tra công cụ thực thi
  const tools: string[] = (stepObj.tool_calls || []).map((t: any) => (t.name || t.tool_name || "").toLowerCase());
  const toolArgsStr = JSON.stringify(stepObj.tool_calls || {}).toLowerCase();

  // 1. Cổng 7: Xuất Bản YouTube
  if (
    toolArgsStr.includes("youtube_publisher") ||
    toolArgsStr.includes("upload_unlisted_video") ||
    toolArgsStr.includes("publishing_kit") ||
    text.includes("đã đăng tải youtube") ||
    text.includes("cổng 7") ||
    text.includes("gate 7") ||
    text.includes("xuất bản youtube")
  ) {
    return {
      gateNumber: 7,
      gateName: "Cổng 7: Xuất Bản YouTube (Unlisted)",
      progressPercent: 100,
      isCompleted: true,
    };
  }

  // 2. Cổng 6 HOÀN THÀNH (Master Film & 3D Thumbnail đã render xong)
  if (
    text.includes("hoàn thành sản xuất") ||
    text.includes("video thành phẩm đã sẵn sàng") ||
    text.includes("video render thành công") ||
    text.includes("đã hoàn thành video") ||
    (text.includes("production of the video") && text.includes("is complete")) ||
    text.includes("trích xuất preview") ||
    text.includes("final product adheres") ||
    (toolArgsStr.includes("ffmpeg") && text.includes("mp4") && text.includes("sẵn sàng"))
  ) {
    return {
      gateNumber: 6,
      gateName: "Cổng 6: Master Film & 3D Thumb (Hoàn Thành)",
      progressPercent: 100,
      isCompleted: true,
    };
  }

  // 3. Cổng 6 ĐANG BẤM MÁY (Dựng video qua FFmpeg, make_threads_video, compositor)
  if (
    toolArgsStr.includes("make_threads_video") ||
    (toolArgsStr.includes("produce_threads") && toolArgsStr.includes("python")) ||
    toolArgsStr.includes("master_assembly") ||
    toolArgsStr.includes("assemble_104_master_film") ||
    (toolArgsStr.includes("ffmpeg") && (toolArgsStr.includes("output/threads") || toolArgsStr.includes("output/cinematic"))) ||
    text.includes("ghép nối video hoàn chỉnh") ||
    text.includes("bấm máy") ||
    text.includes("cổng 6") ||
    text.includes("gate 6")
  ) {
    return {
      gateNumber: 6,
      gateName: "Cổng 6: Bấm Máy & Lắp Ráp Master",
      progressPercent: 85,
      isCompleted: false,
    };
  }

  // 4. Cổng 5: Khung Hình Storyboard & Card PNG
  if (
    toolArgsStr.includes("render_card") ||
    toolArgsStr.includes("card_engine") ||
    toolArgsStr.includes("generate_storyboard_frames") ||
    toolArgsStr.includes("storyboard") ||
    toolArgsStr.includes("cutout") ||
    text.includes("cổng 5") ||
    text.includes("gate 5") ||
    text.includes("render thẻ")
  ) {
    return {
      gateNumber: 5,
      gateName: "Cổng 5: Khung Storyboard & Card PNG",
      progressPercent: 70,
      isCompleted: true,
    };
  }

  // 5. Cổng 4: Lồng Tiếng Edge-TTS 48kHz
  if (
    toolArgsStr.includes("edge_tts") ||
    toolArgsStr.includes("synthesize_speech") ||
    toolArgsStr.includes("gate4_audio_runner") ||
    toolArgsStr.includes("sinh âm thanh") ||
    text.includes("sinh âm thanh cho post") ||
    text.includes("sinh âm thanh cho comment") ||
    text.includes("cổng 4") ||
    text.includes("gate 4") ||
    text.includes("lồng tiếng")
  ) {
    return {
      gateNumber: 4,
      gateName: "Cổng 4: Lồng Tiếng Edge-TTS 48kHz",
      progressPercent: 55,
      isCompleted: true,
    };
  }

  // 6. Cổng 3: Dàn Asset & Avatar Độc Bản
  if (
    toolArgsStr.includes("cache_media") ||
    toolArgsStr.includes("hoangbao_avatars") ||
    toolArgsStr.includes("knhisme_avatars") ||
    toolArgsStr.includes("subway_surfers") ||
    toolArgsStr.includes("post_media") ||
    (toolArgsStr.includes("download") && (toolArgsStr.includes("avatar") || toolArgsStr.includes("meme"))) ||
    text.includes("cổng 3") ||
    text.includes("gate 3") ||
    text.includes("bộ asset") ||
    text.includes("dàn asset")
  ) {
    return {
      gateNumber: 3,
      gateName: "Cổng 3: Bộ Asset & Dàn Avatar Độc Bản",
      progressPercent: 40,
      isCompleted: true,
    };
  }

  // 7. Cổng 2: Phê Duyệt Kịch Bản 5 Hồi & Thoại
  if (
    (toolArgsStr.includes("produce_threads") && (toolArgsStr.includes("write_file") || toolArgsStr.includes("edit_file"))) ||
    toolArgsStr.includes("thread_data") ||
    toolArgsStr.includes("beats") ||
    text.includes("kịch bản 5 hồi") ||
    text.includes("tts_content") ||
    text.includes("phê duyệt kịch bản") ||
    text.includes("cổng 2") ||
    text.includes("gate 2")
  ) {
    return {
      gateNumber: 2,
      gateName: "Cổng 2: Phê Duyệt Kịch Bản & Thoại",
      progressPercent: 25,
      isCompleted: true,
    };
  }

  // 8. Cổng 1: Tiếp Nhận Ý Tưởng & Phân Tích Đề Tài
  if (
    stepObj.type === "USER_INPUT" ||
    text.includes("dispatch_web") ||
    text.includes("hãy sản xuất video") ||
    toolArgsStr.includes("scraper") ||
    toolArgsStr.includes("fetch_thread") ||
    toolArgsStr.includes("puppeteer_navigate") ||
    text.includes("tiếp nhận yêu cầu sản xuất") ||
    text.includes("cổng 1") ||
    text.includes("gate 1")
  ) {
    return {
      gateNumber: 1,
      gateName: "Cổng 1: Tiếp Nhận Ý Tưởng & Phân Tích",
      progressPercent: 15,
      isCompleted: true,
    };
  }

  // Không có bằng chứng chuyển cổng -> Trả về null để KHÔNG làm thụt lùi tiến độ về Cổng 1
  return null;
}

/**
 * Tính toán trạng thái tổng thể hiện tại của Quy Trình 7 Cổng (Studio State Tracker)
 * Quét toàn bộ ngữ cảnh gần nhất và đối chiếu với file thành phẩm trên đĩa
 */
export function getProductionStudioState(convoId?: string): ProductionStudioState {
  const session = getAntigravitySession(convoId);
  const now = new Date().toISOString();

  // Kiểm tra file video mới render trong output/threads hoặc output/cinematic
  let latestMp4: { path: string; mtime: number; name: string } | null = null;
  const searchDirs = [
    join(process.cwd(), "output", "threads"),
    join(process.cwd(), "output", "cinematic")
  ];

  for (const sDir of searchDirs) {
    if (!existsSync(sDir)) continue;
    try {
      const items = readdirSync(sDir);
      for (const item of items) {
        const full = join(sDir, item);
        const st = statSync(full);
        if (st.isDirectory()) {
          const subFiles = readdirSync(full);
          const mp4 = subFiles.find(f => f.endsWith(".mp4"));
          if (mp4) {
            const mp4Full = join(full, mp4);
            const mp4Time = statSync(mp4Full).mtimeMs;
            if (!latestMp4 || mp4Time > latestMp4.mtime) {
              latestMp4 = { path: mp4Full, mtime: mp4Time, name: item };
            }
          }
        } else if (item.endsWith(".mp4")) {
          if (!latestMp4 || st.mtimeMs > latestMp4.mtime) {
            latestMp4 = { path: full, mtime: st.mtimeMs, name: item };
          }
        }
      }
    } catch (_) {}
  }

  // Mặc định ban đầu
  let currentGate = 1;
  let gateName = "Cổng 1: Tiếp Nhận Ý Tưởng & Phân Tích";
  let progressPercent = 15;
  let isCompleted = false;
  const completedGatesSet = new Set<number>();
  let activeJobId = latestMp4 ? latestMp4.name : undefined;

  if (session && existsSync(session.transcriptPath)) {
    try {
      const raw = readFileSync(session.transcriptPath, "utf-8");
      const lines = raw.trim().split("\n").filter(Boolean);
      
      // Quét 100 dòng gần nhất để lần theo dấu vết các cổng đã qua
      const recentLines = lines.slice(Math.max(0, lines.length - 100));
      for (const line of recentLines) {
        try {
          const obj = JSON.parse(line);
          const g = inferProductionGate(obj);
          if (g) {
            if (g.gateNumber >= currentGate) {
              currentGate = g.gateNumber;
              gateName = g.gateName;
              progressPercent = g.progressPercent;
              if (g.isCompleted) isCompleted = true;
            }
            // Đánh dấu các cổng trước đó là đã hoàn thành
            for (let k = 1; k <= g.gateNumber; k++) {
              if (k < g.gateNumber || g.isCompleted) {
                completedGatesSet.add(k);
              }
            }
          }
        } catch (_) {}
      }
    } catch (_) {}
  }

  // Nếu trên đĩa đã có file video MP4 render trong vòng 2 giờ qua và đang ở Cổng 6
  const twoHoursAgo = Date.now() - 2 * 60 * 60 * 1000;
  if (latestMp4 && latestMp4.mtime > twoHoursAgo) {
    if (currentGate <= 6) {
      currentGate = 6;
      gateName = "Cổng 6: Master Film & 3D Thumb (Hoàn Thành)";
      progressPercent = 100;
      isCompleted = true;
      for (let k = 1; k <= 6; k++) {
        completedGatesSet.add(k);
      }
    }
  }

  return {
    currentGate,
    gateName,
    progressPercent,
    isCompleted,
    completedGates: Array.from(completedGatesSet).sort((a, b) => a - b),
    activeJobId,
    masterVideoPath: latestMp4 ? latestMp4.path : undefined,
    lastUpdated: now,
  };
}

/**
 * Đọc N bước gần nhất từ file transcript.jsonl
 */
export function getRecentTranscriptEvents(convoId?: string, limit: number = 30): TranscriptEvent[] {
  const session = getAntigravitySession(convoId);
  if (!session || !existsSync(session.transcriptPath)) return [];

  try {
    const raw = readFileSync(session.transcriptPath, "utf-8");
    const lines = raw.trim().split("\n").filter(Boolean);
    const startIdx = Math.max(0, lines.length - limit);
    const slice = lines.slice(startIdx);

    const events: TranscriptEvent[] = [];
    for (const line of slice) {
      try {
        const obj = JSON.parse(line);
        const tools: string[] = [];
        const toolDetails: Array<{ name: string; summary?: string; command?: string }> = [];

        if (obj.tool_calls && Array.isArray(obj.tool_calls)) {
          for (const tc of obj.tool_calls) {
            const toolName = tc.name || tc.tool_name || "";
            tools.push(toolName);
            const args = tc.args || tc.arguments || {};
            let cmd: string | undefined = undefined;
            if (args.CommandLine) {
              const cl = String(args.CommandLine).replace(/^"|"$/g, "");
              cmd = cl.slice(0, 160);
            }
            let summary = args.toolSummary ? String(args.toolSummary).replace(/^"|"$/g, "") : undefined;
            if (!summary && toolName === "read_file" && args.Path) {
              summary = `Read ${String(args.Path).replace(/^"|"$/g, "")}`;
            } else if (!summary && toolName === "write_file" && args.Path) {
              summary = `Write ${String(args.Path).replace(/^"|"$/g, "")}`;
            } else if (!summary && toolName === "edit_file" && args.Path) {
              summary = `Edit ${String(args.Path).replace(/^"|"$/g, "")}`;
            }
            toolDetails.push({
              name: toolName,
              summary: summary || cmd,
              command: cmd,
            });
          }
        }

        const gate = inferProductionGate(obj);

        let contentPreview = "";
        if (typeof obj.content === "string") {
          contentPreview = obj.content.slice(0, 200).replace(/\n+/g, " ");
        }

        let thoughtPreview: string | undefined = undefined;
        if (typeof obj.thinking === "string") {
          thoughtPreview = obj.thinking.slice(0, 250).replace(/\n+/g, " ");
        }

        events.push({
          stepIndex: obj.step_index || 0,
          type: obj.type || "UNKNOWN",
          status: obj.status || "UNKNOWN",
          timestamp: obj.created_at || new Date().toISOString(),
          thought: thoughtPreview,
          tools: tools.length ? tools : undefined,
          toolDetails: toolDetails.length ? toolDetails : undefined,
          gate,
          contentPreview: contentPreview || undefined,
        });
      } catch {
        // Skip unparseable line
      }
    }

    return events;
  } catch (err) {
    console.error("[AntigravityBridge] Lỗi đọc transcript.jsonl:", err);
    return [];
  }
}

/**
 * Gửi lệnh điều khiển trực tiếp vào Antigravity IDE thông qua agentapi.bat
 */
export function dispatchAntigravityMessage(convoId: string, message: string): Promise<{ success: boolean; output: string }> {
  return new Promise((resolve) => {
    if (!existsSync(AGENTAPI_BAT)) {
      resolve({ success: false, output: `Không tìm thấy agentapi.bat tại ${AGENTAPI_BAT}` });
      return;
    }

    const safeMsg = '"' + message.replace(/"/g, '""').replace(/[\r\n]+/g, ' ') + '"';
    const args = ["send-message", convoId, safeMsg];
    const proc = spawn(AGENTAPI_BAT, args, { shell: true, windowsHide: true });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", d => (stdout += d.toString()));
    proc.stderr.on("data", d => (stderr += d.toString()));

    proc.on("close", (code) => {
      if (code === 0) {
        resolve({ success: true, output: stdout || "Đã gửi thông điệp thành công tới Antigravity IDE." });
      } else {
        resolve({ success: false, output: stderr || stdout || `Lỗi thực thi mã ${code}` });
      }
    });

    proc.on("error", (err) => {
      resolve({ success: false, output: err.message });
    });
  });
}
