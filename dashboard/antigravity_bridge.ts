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

/**
 * Suy luận Cổng sản xuất (Gate 1 -> Gate 7) từ nội dung của bước thực thi
 */
export function inferProductionGate(stepObj: any): { gateNumber: number; gateName: string; progressPercent: number } {
  const content = (stepObj.content || "").toLowerCase();
  const thinking = (stepObj.thinking || "").toLowerCase();
  const text = `${content} ${thinking}`;

  // Kiểm tra công cụ thực thi
  const tools: string[] = (stepObj.tool_calls || []).map((t: any) => (t.name || t.tool_name || "").toLowerCase());
  const toolArgsStr = JSON.stringify(stepObj.tool_calls || {}).toLowerCase();

  if (toolArgsStr.includes("youtube") || toolArgsStr.includes("upload_unlisted_video") || text.includes("cổng 7") || text.includes("gate 7") || text.includes("xuất bản youtube")) {
    return { gateNumber: 7, gateName: "Cổng 7: Xuất Bản YouTube", progressPercent: 100 };
  }
  if (toolArgsStr.includes("make_threads_video") || toolArgsStr.includes("master_assembly") || toolArgsStr.includes("ffmpeg") && (toolArgsStr.includes("output/threads") || toolArgsStr.includes("output/cinematic")) || text.includes("cổng 6") || text.includes("gate 6") || text.includes("bấm máy")) {
    return { gateNumber: 6, gateName: "Cổng 6: Bấm Máy & Lắp Ráp Master", progressPercent: 85 };
  }
  if (toolArgsStr.includes("render_card") || toolArgsStr.includes("storyboard") || toolArgsStr.includes("cutout") || text.includes("cổng 5") || text.includes("gate 5")) {
    return { gateNumber: 5, gateName: "Cổng 5: Khung Hình Storyboard & Card", progressPercent: 70 };
  }
  if (toolArgsStr.includes("edge_tts") || toolArgsStr.includes("synthesize_speech") || toolArgsStr.includes("cổng 4") || text.includes("cổng 4") || text.includes("gate 4") || text.includes("lồng tiếng")) {
    return { gateNumber: 4, gateName: "Cổng 4: Lồng Tiếng Edge-TTS 48kHz", progressPercent: 55 };
  }
  if (toolArgsStr.includes("cache_media") || toolArgsStr.includes("download") || toolArgsStr.includes("avatar") || text.includes("cổng 3") || text.includes("gate 3") || text.includes("asset")) {
    return { gateNumber: 3, gateName: "Cổng 3: Duyệt Dàn Asset & Avatar", progressPercent: 40 };
  }
  if (text.includes("kịch bản") || text.includes("dialogue") || text.includes("5 hồi") || text.includes("cổng 2") || text.includes("gate 2")) {
    return { gateNumber: 2, gateName: "Cổng 2: Phê Duyệt Kịch Bản & Thoại", progressPercent: 25 };
  }

  return { gateNumber: 1, gateName: "Cổng 1: Tiếp Nhận Ý Tưởng & Phân Tích", progressPercent: 10 };
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

    const args = ["send-message", convoId, message];
    const proc = spawn(AGENTAPI_BAT, args, { shell: true });

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
