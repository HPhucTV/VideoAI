import { createServer, IncomingMessage, ServerResponse } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { readFile, writeFile, unlink, readdir, mkdir, rm } from "node:fs/promises";
import { join, extname, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import {
  getActiveConversationId,
  getAntigravitySession,
  getRecentTranscriptEvents,
  getProductionStudioState,
  dispatchAntigravityMessage,
} from "./antigravity_bridge.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = join(__dirname, "..");
const PORT = parseInt(process.env.PORT || "3333", 10);
const OUTPUT_DIR = join(ROOT_DIR, "output");
const JOBS_DIR = join(OUTPUT_DIR, "jobs");
const PUBLIC_DIR = join(__dirname, "public");

const MIME_TYPES: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".mp4": "video/mp4",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".vtt": "text/vtt; charset=utf-8",
  ".srt": "text/plain; charset=utf-8",
  ".ico": "image/x-icon",
};

function sendJson(res: ServerResponse, status: number, data: any) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  });
  res.end(JSON.stringify(data));
}

function parseBody(req: IncomingMessage): Promise<any> {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", chunk => (body += chunk));
    req.on("end", () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (err) {
        reject(err);
      }
    });
    req.on("error", reject);
  });
}

function streamFileWithRanges(filePath: string, req: IncomingMessage, res: ServerResponse) {
  if (!existsSync(filePath)) {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
    return;
  }

  const stat = statSync(filePath);
  const fileSize = stat.size;
  const ext = extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  const range = req.headers.range;
  if (range) {
    const parts = range.replace(/bytes=/, "").split("-");
    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

    if (start >= fileSize) {
      res.writeHead(416, {
        "Content-Range": `bytes */${fileSize}`,
      });
      res.end();
      return;
    }

    const chunksize = end - start + 1;
    const fileStream = createReadStream(filePath, { start, end });

    res.writeHead(206, {
      "Content-Range": `bytes ${start}-${end}/${fileSize}`,
      "Accept-Ranges": "bytes",
      "Content-Length": chunksize,
      "Content-Type": contentType,
      "Access-Control-Allow-Origin": "*",
    });

    fileStream.pipe(res);
  } else {
    res.writeHead(200, {
      "Content-Length": fileSize,
      "Content-Type": contentType,
      "Accept-Ranges": "bytes",
      "Access-Control-Allow-Origin": "*",
    });

    createReadStream(filePath).pipe(res);
  }
}

async function scanVideoLibrary() {
  await mkdir(JOBS_DIR, { recursive: true });
  const jobFiles = (await readdir(JOBS_DIR)).filter(f => f.endsWith(".json"));
  const videos: any[] = [];

  for (const file of jobFiles) {
    const jobPath = join(JOBS_DIR, file);
    try {
      const content = await readFile(jobPath, "utf-8");
      const job = JSON.parse(content);
      const id = job.jobId || basename(file, ".json");
      const workshop = job.workshop || "explainer";

      // Tìm file video MP4 thành phẩm
      let videoFile: string | null = null;
      let thumbFile: string | null = null;
      let srtFile: string | null = null;

      const candidates = [
        join(OUTPUT_DIR, workshop, `${id}.mp4`),
        join(OUTPUT_DIR, workshop, `${id}-sub.mp4`),
        join(OUTPUT_DIR, workshop, "video.mp4"),
      ];

      for (const cand of candidates) {
        if (existsSync(cand)) {
          videoFile = cand;
          break;
        }
      }

      // Tìm ảnh đại diện Thumbnail
      const thumbCandidates = [
        join(OUTPUT_DIR, workshop, `${id}-thumb.png`),
        join(OUTPUT_DIR, workshop, `${id}-sub-thumb.png`),
        join(OUTPUT_DIR, workshop, "sample-still.png"),
        join(OUTPUT_DIR, workshop, "test-still.png"),
      ];

      for (const cand of thumbCandidates) {
        if (existsSync(cand)) {
          thumbFile = cand;
          break;
        }
      }

      // Tìm file phụ đề SRT
      const srtCandidates = [
        join(OUTPUT_DIR, workshop, id, "input.srt"),
        join(OUTPUT_DIR, workshop, `${id}.srt`),
        join(OUTPUT_DIR, "news", "caption.txt"),
      ];

      for (const cand of srtCandidates) {
        if (existsSync(cand)) {
          srtFile = cand;
          break;
        }
      }

      let sizeBytes = 0;
      let mtime = statSync(jobPath).mtime;
      if (videoFile && existsSync(videoFile)) {
        const vstat = statSync(videoFile);
        sizeBytes = vstat.size;
        mtime = vstat.mtime;
      }

      const possibleKit = join(OUTPUT_DIR, workshop, id, "publishing_kit.json");
      let publishingKit = job.publishingKit || null;
      if (!publishingKit && existsSync(possibleKit)) {
        try {
          publishingKit = JSON.parse(await readFile(possibleKit, "utf-8"));
        } catch (_) {}
      }

      videos.push({
        id,
        title: job.title || id,
        workshop,
        archetype: job.archetype || "explainer",
        targetPlatform: job.targetPlatform || "tiktok",
        canvas: job.canvas || { width: 1080, height: 1920, fps: (workshop === "explainer" || workshop === "whiteboard") ? 90 : 60 },
        voice: job.voice || { voiceId: "vi-VN-NamMinhNeural" },
        beatsCount: job.beats?.length || 0,
        beats: job.beats || [],
        metadata: job.metadata || {},
        publishingKit,
        hasVideo: Boolean(videoFile),
        videoUrl: videoFile ? `/media/${workshop}/${encodeURIComponent(basename(videoFile))}` : null,
        thumbUrl: thumbFile ? `/media/${workshop}/${encodeURIComponent(basename(thumbFile))}` : null,
        srtUrl: srtFile ? `/media/${workshop}/${encodeURIComponent(id)}/input.srt` : null,
        sizeBytes,
        lastModified: mtime.toISOString(),
      });
    } catch (e) {
      console.warn(`[WARN] Khong the doc file job: ${file}`, e);
    }
  }

  // Quét thêm thư mục output/threads (Xưởng 5) và output/cinematic (Xưởng 4)
  const extraWorkshops = ["threads", "cinematic"];
  for (const ws of extraWorkshops) {
    const wsDir = join(OUTPUT_DIR, ws);
    if (!existsSync(wsDir)) continue;

    try {
      const items = await readdir(wsDir, { withFileTypes: true });
      for (const item of items) {
        let vPath: string | null = null;
        let vId = item.name;

        if (item.isDirectory()) {
          // Ví dụ: output/threads/job_thread_knhisme_phuhuynh_fuck/job_thread_knhisme_phuhuynh_fuck.mp4
          const subFiles = await readdir(join(wsDir, item.name));
          const mp4 = subFiles.find(f => f.endsWith(".mp4"));
          if (mp4) {
            vPath = join(wsDir, item.name, mp4);
            vId = item.name;
          }
        } else if (item.isFile() && item.name.endsWith(".mp4")) {
          vPath = join(wsDir, item.name);
          vId = basename(item.name, ".mp4");
        }

        if (vPath && existsSync(vPath) && !videos.some(v => v.id === vId)) {
          const vstat = statSync(vPath);
          const relVideoUrl = `/media/${ws}/${item.isDirectory() ? encodeURIComponent(item.name) + "/" + encodeURIComponent(basename(vPath)) : encodeURIComponent(basename(vPath))}`;
          let relThumbUrl: string | null = null;
          let publishingKit: any = null;
          if (item.isDirectory()) {
            const possibleThumb = ["thumb.jpg", "thumb.png", "thumbnail.jpg"].find(t => existsSync(join(wsDir, item.name, t)));
            if (possibleThumb) {
              relThumbUrl = `/media/${ws}/${encodeURIComponent(item.name)}/${possibleThumb}`;
            }

            const possibleKits = [
              join(wsDir, item.name, "publishing_kit.json"),
              join(wsDir, item.name, `${item.name}_publishing_kit.json`),
            ];
            for (const pk of possibleKits) {
              if (existsSync(pk)) {
                try {
                  publishingKit = JSON.parse(await readFile(pk, "utf-8"));
                  break;
                } catch (_) {}
              }
            }
          }
          videos.push({
            id: vId,
            title: vId.replace(/job_thread_/g, "Threads: ").replace(/job-/g, "Job: ").replace(/_/g, " "),
            workshop: ws,
            archetype: ws === "threads" ? "social_drama" : "cinematic_3d",
            targetPlatform: ws === "threads" ? "tiktok" : "youtube_long",
            canvas: { width: ws === "threads" ? 1080 : 1920, height: ws === "threads" ? 1920 : 1080, fps: 60 },
            voice: { voiceId: "vi-VN-NamMinhNeural" },
            beatsCount: ws === "threads" ? 6 : 12,
            beats: [],
            metadata: { engine: ws === "threads" ? "Chroma Key & Headless Chrome" : "FlowKit & Imagen/Veo" },
            publishingKit,
            hasVideo: true,
            videoUrl: relVideoUrl,
            thumbUrl: relThumbUrl,
            srtUrl: null,
            sizeBytes: vstat.size,
            lastModified: vstat.mtime.toISOString(),
          });
        }
      }
    } catch (e) {
      console.warn(`[WARN] Khong the scan thu muc ${ws}:`, e);
    }
  }

  // Sắp xếp video mới nhất lên đầu
  videos.sort((a, b) => new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime());
  return videos;
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url || "/", `http://${req.headers.host}`);
  let pathname = url.pathname;
  try {
    pathname = decodeURIComponent(url.pathname);
  } catch {
    // Keep raw pathname if decoding fails
  }

  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    });
    res.end();
    return;
  }

  // ================= ANTIGRAVITY 2.0 LIVE BRIDGE APIS =================
  if (pathname === "/api/antigravity/status" && req.method === "GET") {
    const session = getAntigravitySession();
    const studioState = getProductionStudioState(session?.conversationId);
    sendJson(res, 200, {
      success: true,
      connected: Boolean(session),
      session,
      studioState,
    });
    return;
  }

  if (pathname === "/api/antigravity/events" && req.method === "GET") {
    const limit = parseInt(url.searchParams.get("limit") || "35", 10);
    const events = getRecentTranscriptEvents(undefined, limit);
    sendJson(res, 200, {
      success: true,
      events,
    });
    return;
  }

  if (pathname === "/api/antigravity/stream") {
    res.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "Connection": "keep-alive",
      "Access-Control-Allow-Origin": "*",
    });

    const sendSse = (event: string, data: any) => {
      res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
    };

    let session = getAntigravitySession();
    let initialStudioState = getProductionStudioState(session?.conversationId);
    sendSse("init", { connected: Boolean(session), session, studioState: initialStudioState });
    sendSse("gate_state", initialStudioState);

    let lastSize = session ? session.transcriptSize : 0;
    let lastStep = 0;

    // Gửi lịch sử gần nhất
    const initEvents = getRecentTranscriptEvents(undefined, 15);
    if (initEvents.length > 0) {
      lastStep = initEvents[initEvents.length - 1].stepIndex;
      sendSse("history", { events: initEvents });
    }

    const pollInterval = setInterval(() => {
      try {
        const curSession = getAntigravitySession();
        if (!curSession) {
          sendSse("status", { connected: false });
          return;
        }

        // Đồng bộ trạng thái 7 Cổng định kỳ
        const curState = getProductionStudioState(curSession.conversationId);
        sendSse("gate_state", curState);

        if (curSession.transcriptSize !== lastSize) {
          lastSize = curSession.transcriptSize;
          const freshEvents = getRecentTranscriptEvents(curSession.conversationId, 10);
          const newEvents = freshEvents.filter(e => e.stepIndex > lastStep);
          if (newEvents.length > 0) {
            lastStep = newEvents[newEvents.length - 1].stepIndex;
            for (const ev of newEvents) {
              sendSse("step", ev);
            }
          }
        }
      } catch (err) {
        // Silent catch for poll error
      }
    }, 1200);

    const pingInterval = setInterval(() => {
      res.write(": keep-alive\n\n");
    }, 15000);

    req.on("close", () => {
      clearInterval(pollInterval);
      clearInterval(pingInterval);
    });
    return;
  }

  if (pathname === "/api/antigravity/dispatch" && req.method === "POST") {
    try {
      const body = await parseBody(req);
      const prompt = body.prompt;
      if (!prompt) {
        sendJson(res, 400, { success: false, error: "Thiếu prompt yêu cầu" });
        return;
      }
      const convoId = body.conversationId || getActiveConversationId();
      if (!convoId) {
        sendJson(res, 500, { success: false, error: "Không tìm thấy phiên Antigravity nào đang hoạt động" });
        return;
      }

      const result = await dispatchAntigravityMessage(convoId, prompt);
      sendJson(res, result.success ? 200 : 500, result);
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname === "/api/antigravity/approve" && req.method === "POST") {
    try {
      const body = await parseBody(req);
      const gate = body.gate || "Gate 3";
      const convoId = body.conversationId || getActiveConversationId();
      if (!convoId) {
        sendJson(res, 500, { success: false, error: "Không tìm thấy phiên Antigravity nào đang hoạt động" });
        return;
      }

      const approvalMsg = `[Phê duyệt từ Web Dashboard]: Đã duyệt ${gate}. Cho phép tiếp tục tiến trình sản xuất video sang cổng kế tiếp!`;
      const result = await dispatchAntigravityMessage(convoId, approvalMsg);
      sendJson(res, result.success ? 200 : 500, result);
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // --- YOUTUBE PUBLISHER APIS ---
  if (pathname === "/api/youtube/channels" && req.method === "GET") {
    try {
      const channelsDir = join(ROOT_DIR, "workshops", "workshop-cinematic", "youtube", "channels");
      const channels: Array<{ id: string; name: string; hasToken: boolean }> = [];
      if (existsSync(channelsDir)) {
        const dirs = await readdir(channelsDir, { withFileTypes: true });
        for (const d of dirs) {
          if (d.isDirectory()) {
            const hasToken = existsSync(join(channelsDir, d.name, "token.json"));
            channels.push({
              id: d.name,
              name: d.name === "HanShin - Thread" ? "HanShin - Thread (Verified Shorts)" : d.name,
              hasToken,
            });
          }
        }
      }
      sendJson(res, 200, { success: true, channels });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname === "/api/youtube/upload" && req.method === "POST") {
    try {
      const body = await parseBody(req);
      const { jobId, channel = "HanShin", title, description = "", tags = "", privacy = "unlisted", category = "24" } = body;
      if (!jobId || !title) {
        sendJson(res, 400, { success: false, error: "Thiếu jobId hoặc title" });
        return;
      }

      // Tìm kiếm video file trên ổ đĩa
      let videoPath = "";
      let thumbPath = "";
      let srtPath = "";

      const candidateDirs = [
        join(OUTPUT_DIR, "threads", jobId),
        join(OUTPUT_DIR, "cinematic", jobId),
        join(OUTPUT_DIR, "explainer"),
        join(OUTPUT_DIR, "whiteboard", jobId),
        join(OUTPUT_DIR, "news"),
      ];

      for (const dir of candidateDirs) {
        if (!existsSync(dir)) continue;
        const candidateMp4s = [
          join(dir, `${jobId}.mp4`),
          join(dir, `${jobId}_master.mp4`),
          join(dir, "master.mp4"),
        ];
        for (const mp4 of candidateMp4s) {
          if (existsSync(mp4)) {
            videoPath = mp4;
            break;
          }
        }
        if (videoPath) {
          const candidateThumbs = [
            join(dir, "thumb.jpg"),
            join(dir, "thumb.png"),
            join(dir, "thumbnail_3d.jpg"),
            join(dir, "preview_post_perfect_avatar.jpg"),
            join(dir, `${jobId}.jpg`),
          ];
          for (const th of candidateThumbs) {
            if (existsSync(th)) {
              thumbPath = th;
              break;
            }
          }
          const candidateSrts = [
            join(dir, `${jobId}.srt`),
            join(dir, "captions.srt"),
          ];
          for (const srt of candidateSrts) {
            if (existsSync(srt)) {
              srtPath = srt;
              break;
            }
          }
          break;
        }
      }

      if (!videoPath) {
        sendJson(res, 404, { success: false, error: `Không tìm thấy file video MP4 của job ${jobId}` });
        return;
      }

      const pyExe = join(ROOT_DIR, "workshops", "workshop-cinematic", ".venv", "Scripts", "python.exe");
      const actualPy = existsSync(pyExe) ? pyExe : "python";

      const pyArgs = [
        join(ROOT_DIR, "scripts", "youtube_publisher.py"),
        "--channel", channel,
        "--video", videoPath,
        "--title", title,
        "--description", description,
        "--privacy", privacy,
        "--category", category,
        "--json",
      ];
      if (tags) {
        pyArgs.push("--tags", tags);
      }
      if (thumbPath) {
        pyArgs.push("--thumb", thumbPath);
      }
      if (srtPath) {
        pyArgs.push("--srt", srtPath);
      }

      const proc = spawn(actualPy, pyArgs, { cwd: ROOT_DIR });
      let stdout = "";
      let stderr = "";

      proc.stdout.on("data", d => (stdout += d.toString()));
      proc.stderr.on("data", d => (stderr += d.toString()));

      proc.on("close", code => {
        if (code === 0) {
          try {
            const data = JSON.parse(stdout.trim());
            sendJson(res, 200, data);
          } catch {
            sendJson(res, 200, { success: true, raw: stdout.trim() });
          }
        } else {
          sendJson(res, 500, { success: false, error: stderr.trim() || stdout.trim() || `Exit code ${code}` });
        }
      });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname === "/api/youtube/suggest-seo" && req.method === "POST") {
    try {
      const body = await parseBody(req);
      const { jobId } = body;
      if (!jobId) {
        sendJson(res, 400, { success: false, error: "Thiếu jobId" });
        return;
      }

      // Tìm video trong thư viện
      const videos = await scanVideoLibrary();
      const video = videos.find(v => v.id === jobId);
      const rawTitle = video ? video.title : jobId;
      const ws = video ? video.workshop : "threads";

      // Tạo gợi ý thông minh dựa trên thể loại
      let kit: any = null;
      if (ws === "threads") {
        const cleanTitle = rawTitle.replace(/^Threads:\s*/i, "").trim();
        kit = {
          title: `🔥 KHI BẠN THÂN ${cleanTitle.toUpperCase()}... CÁI KẾT XỈU NGANG! 🤡 #Shorts #Threads`,
          title_options: [
            `🔥 KHI BẠN THÂN ${cleanTitle.toUpperCase()}... CÁI KẾT XỈU NGANG! 🤡 #Shorts #Threads`,
            `Drama Bạn Thân: ${cleanTitle} - Đúng là 'bạn thân ai nấy lo' 💔 #Shorts #DramaVN`,
            `Tâm Sự Threads: ${cleanTitle} #Shorts #HanShin #HaiHuoc #GiaiTri`
          ],
          description: `Ủa bạn thân mà làm vậy coi được hả trời?! Câu chuyện ${cleanTitle} được tái hiện sinh động bằng AI & Remotion NLE.\n\nTheo dõi kênh @HanShin-g8i để cập nhật drama Threads viral mỗi ngày!\n\n00:00 - Tình bạn diệu kỳ & Mở đầu\n00:10 - Tình huống trớ trêu\n00:25 - Cú twist bất ngờ\n00:38 - Cái kết cười xỉu\n\n#HanShin #Threads #Shorts #BanThan #HaiHuoc #DramaVN #MinecraftParkour`,
          tags: ["HanShin", "Threads", "Shorts", "Ban Than", "Drama VN", "Hai Huoc", "Giai Tri", "Minecraft Parkour", "Gen Z", "TikTok Viral"],
          category: "24",
          privacy: "unlisted"
        };
      } else {
        const cleanTitle = rawTitle.replace(/^Job:\s*/i, "").trim();
        kit = {
          title: `${cleanTitle} | Toàn Cảnh & Phân Tích Chuyên Sâu 4K`,
          title_options: [
            `${cleanTitle} | Toàn Cảnh & Phân Tích Chuyên Sâu 4K`,
            `Bí Mật Đằng Sau ${cleanTitle} Mà Bạn Chưa Từng Biết!`,
            `Giải Mã ${cleanTitle}: Bản Điện Ảnh Hoạt Họa 3D Chuẩn Quốc Tế`
          ],
          description: `Tập phim điện ảnh 3D phân tích chuyên sâu về ${cleanTitle}.\n\n00:00 - Giới thiệu tổng quan\n01:30 - Phân tích bối cảnh cốt lõi\n03:45 - Cao trào & Giải pháp đột phá\n06:00 - Kết luận & Định hướng tương lai\n\n#OmniVideo #Phim3D #DoHoa4K #Tech #KienThuc #GiaiMaTech`,
          tags: ["OmniVideo", "Phim 3D", "Cong Nghe", "AI", "Do Hoa 4K", "Veo2", "Giai Ma Tech"],
          category: "28",
          privacy: "unlisted"
        };
      }

      // Lưu file publishing_kit.json vào thư mục của job nếu có
      const jobDir = join(OUTPUT_DIR, ws, jobId);
      if (existsSync(jobDir)) {
        await writeFile(join(jobDir, "publishing_kit.json"), JSON.stringify(kit, null, 2), "utf-8");
      }

      sendJson(res, 200, { success: true, publishingKit: kit });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // 1. Phục vụ Media từ thư mục output/
  if (pathname.startsWith("/media/")) {
    const relPath = pathname.replace("/media/", "");
    const filePath = join(OUTPUT_DIR, relPath);
    streamFileWithRanges(filePath, req, res);
    return;
  }

  // 2. REST API Quản lý Kho Video
  if (pathname === "/api/videos" && req.method === "GET") {
    try {
      const videos = await scanVideoLibrary();
      sendJson(res, 200, { success: true, videos });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname.startsWith("/api/videos/") && req.method === "GET") {
    const id = pathname.replace("/api/videos/", "");
    const jobPath = join(JOBS_DIR, `${id}.json`);
    if (!existsSync(jobPath)) {
      sendJson(res, 404, { success: false, error: `Không tìm thấy job ${id}` });
      return;
    }
    try {
      const job = JSON.parse(await readFile(jobPath, "utf-8"));
      sendJson(res, 200, { success: true, job });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname === "/api/videos" && req.method === "POST") {
    try {
      const job = await parseBody(req);
      if (!job.jobId || !job.title) {
        sendJson(res, 400, { success: false, error: "Thiếu jobId hoặc title" });
        return;
      }
      const jobPath = join(JOBS_DIR, `${job.jobId}.json`);
      await writeFile(jobPath, JSON.stringify(job, null, 2), "utf-8");
      sendJson(res, 201, { success: true, jobId: job.jobId });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname.startsWith("/api/videos/") && req.method === "PUT") {
    const id = pathname.replace("/api/videos/", "");
    const jobPath = join(JOBS_DIR, `${id}.json`);
    try {
      const job = await parseBody(req);
      job.jobId = id;
      await writeFile(jobPath, JSON.stringify(job, null, 2), "utf-8");
      sendJson(res, 200, { success: true, jobId: id });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  if (pathname.startsWith("/api/videos/") && req.method === "DELETE") {
    const rawId = pathname.replace("/api/videos/", "");
    const id = decodeURIComponent(rawId).trim();

    if (!id || id.includes("..") || id.includes("/") || id.includes("\\")) {
      sendJson(res, 400, { success: false, error: "ID video không hợp lệ" });
      return;
    }

    try {
      // 1. Xóa file kịch bản job
      const jobPath = join(JOBS_DIR, `${id}.json`);
      if (existsSync(jobPath)) {
        await rm(jobPath, { force: true }).catch(() => {});
      }

      // 2. Lấy danh sách các thư mục xưởng trong output (whiteboard, explainer, news...)
      let workshops = ["whiteboard", "explainer", "news"];
      try {
        const entries = await readdir(OUTPUT_DIR, { withFileTypes: true });
        workshops = entries.filter((e) => e.isDirectory() && e.name !== "jobs").map((e) => e.name);
      } catch {
        // Fallback danh sách cố định
      }

      let deletedItemsCount = 0;

      // 3. Quét từng xưởng để xóa triệt để thư mục phân cảnh & các tệp thành phẩm liên quan
      for (const ws of workshops) {
        const wsDir = join(OUTPUT_DIR, ws);
        if (!existsSync(wsDir)) continue;

        // Xóa thư mục làm việc phân cảnh (ví dụ: output/whiteboard/{id}/)
        const jobDir = join(wsDir, id);
        if (existsSync(jobDir)) {
          await rm(jobDir, { recursive: true, force: true }).catch(() => {});
          deletedItemsCount++;
        }

        // Quét các tệp thành phẩm liên quan (mp4, thumb, srt, vtt, caption, metadata...)
        try {
          const files = await readdir(wsDir);
          for (const f of files) {
            if (f === id || f.startsWith(`${id}.`) || f.startsWith(`${id}-`)) {
              await rm(join(wsDir, f), { recursive: true, force: true }).catch(() => {});
              deletedItemsCount++;
            }
          }
        } catch {
          // Bỏ qua lỗi đọc thư mục con nếu có
        }
      }

      // 4. Quét thư mục gốc output nếu có file/folder liên quan
      try {
        const rootFiles = await readdir(OUTPUT_DIR);
        for (const f of rootFiles) {
          if (f === "jobs") continue;
          if (f === id || f.startsWith(`${id}.`) || f.startsWith(`${id}-`)) {
            await rm(join(OUTPUT_DIR, f), { recursive: true, force: true }).catch(() => {});
            deletedItemsCount++;
          }
        }
      } catch {
        // Bỏ qua
      }

      sendJson(res, 200, {
        success: true,
        message: `Đã xóa thành công kịch bản và toàn bộ tệp liên quan của ${id}`,
        jobId: id,
        deletedItemsCount,
      });
    } catch (err: any) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // 3. API Kích hoạt Re-render với Server-Sent Events (SSE)
  if (pathname.startsWith("/api/render/") && req.method === "GET") {
    const id = pathname.replace("/api/render/", "");
    const jobPath = join(JOBS_DIR, `${id}.json`);

    // Thiết lập SSE Headers trước để trình duyệt nhận stream ngay cả khi gặp lỗi
    res.writeHead(200, {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "Access-Control-Allow-Origin": "*",
    });

    const sendEvent = (event: string, data: any) => {
      res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
    };

    if (!existsSync(jobPath)) {
      sendEvent("error", { text: `Không tìm thấy file kịch bản cho Job: "${id}" tại ${jobPath}` });
      res.end();
      return;
    }

    try {
      const job = JSON.parse(await readFile(jobPath, "utf-8"));
      const workshop = job.workshop || "explainer";

      sendEvent("log", { text: `[1/3] Khởi động render cho Job "${id}" (Phân xưởng: ${workshop})...` });

      if (workshop === "explainer") {
        sendEvent("log", { text: "[2/3] Chuyển đổi kịch bản sang Remotion Props & Tạo giọng đọc TTS..." });

        const adapter = spawn("node", [
          "--experimental-strip-types",
          "workshops/workshop-explainer/src/job-adapter.ts",
          "--job",
          jobPath,
        ], { cwd: ROOT_DIR });

        adapter.stdout.on("data", d => {
          const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
          for (const l of lines) sendEvent("log", { text: l });
        });
        adapter.stderr.on("data", d => {
          const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
          for (const l of lines) sendEvent("log", { text: `[Adapter] ${l}` });
        });

        adapter.on("close", async (code) => {
          if (code !== 0) {
            sendEvent("error", { text: `Adapter thất bại với mã lỗi ${code}` });
            res.end();
            return;
          }

          const isLandscape = job.targetPlatform === "youtube_long" || (job.canvas && job.canvas.width > job.canvas.height);
          const compositionId = isLandscape ? "OmniExplainer-Landscape" : "OmniExplainer-Portrait";

          sendEvent("log", { text: `[3/3] Đang render video với Remotion Engine (${compositionId})...` });

          const outDir = join(OUTPUT_DIR, "explainer");
          await mkdir(outDir, { recursive: true });
          const outVideo = join(outDir, `${id}.mp4`);

          const remotionRender = spawn("npx.cmd", [
            "remotion",
            "render",
            "src/index.ts",
            compositionId,
            `"${outVideo}"`,
            "--props=public/props.json",
            "--gl=angle",
          ], {
            cwd: join(ROOT_DIR, "workshops", "workshop-explainer"),
            shell: true,
          });

          remotionRender.stdout.on("data", d => {
            const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
            for (const l of lines) sendEvent("progress", { text: l });
          });
          remotionRender.stderr.on("data", d => {
            const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
            for (const l of lines) sendEvent("progress", { text: l });
          });

          remotionRender.on("close", (rCode) => {
            if (rCode === 0) {
              sendEvent("done", {
                success: true,
                videoUrl: `/media/explainer/${encodeURIComponent(id)}.mp4`,
                message: "Render video Remotion hoàn tất 100%!",
              });
            } else {
              sendEvent("error", { text: `Remotion render thất bại (mã lỗi: ${rCode})` });
            }
            res.end();
          });
        });
      } else if (workshop === "whiteboard") {
        sendEvent("log", { text: "[2/3] Tổng hợp âm thanh & tạo skeleton phân cảnh Whiteboard..." });
        const outDir = join(OUTPUT_DIR, "whiteboard", id);
        await mkdir(outDir, { recursive: true });
        const pyExe = join(ROOT_DIR, "workshops", "workshop-whiteboard", ".venv", "Scripts", "python.exe");
        const actualPy = existsSync(pyExe) ? pyExe : "python";

        const wbAdapter = spawn(actualPy, [
          "workshops/workshop-whiteboard/scripts/export_video.py",
          id,
        ], { cwd: ROOT_DIR });

        wbAdapter.stdout.on("data", d => {
          const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
          for (const l of lines) sendEvent("log", { text: l });
        });
        wbAdapter.stderr.on("data", d => {
          const lines = d.toString().split("\n").map((l: string) => l.trim()).filter(Boolean);
          for (const l of lines) sendEvent("log", { text: `[Whiteboard] ${l}` });
        });

        wbAdapter.on("close", (wCode) => {
          if (wCode === 0) {
            sendEvent("done", {
              success: true,
              videoUrl: `/media/whiteboard/${encodeURIComponent(id)}.mp4`,
              message: "Đã xuất hoàn chỉnh video bảng trắng 90 FPS!",
            });
          } else {
            sendEvent("error", { text: `Xuất Whiteboard thất bại (mã lỗi: ${wCode})` });
          }
          res.end();
        });
      } else {
        sendEvent("done", { success: true, message: "Kích hoạt phân xưởng thành công!" });
        res.end();
      }
    } catch (err: any) {
      sendEvent("error", { text: err.message });
      res.end();
    }
    return;
  }

  // 4. Phục vụ Static Files cho SPA Frontend (dashboard/public/)
  let reqPath = pathname === "/" ? "/index.html" : pathname;
  let fullPath = join(PUBLIC_DIR, reqPath);

  if (!existsSync(fullPath)) {
    fullPath = join(PUBLIC_DIR, "index.html");
  }

  const ext = extname(fullPath).toLowerCase();
  const contentType = MIME_TYPES[ext] || "text/plain";

  try {
    const data = await readFile(fullPath);
    res.writeHead(200, { "Content-Type": contentType });
    res.end(data);
  } catch (err) {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
  }
});

server.listen(PORT, () => {
  console.log(`\n=============================================================`);
  console.log(`  🎬 OMNIVIDEO STUDIO - VIDEO LIBRARY DASHBOARD LOCAL`);
  console.log(`  Truy cap trinh duyet tai: http://localhost:${PORT}`);
  console.log(`=============================================================\n`);
});
