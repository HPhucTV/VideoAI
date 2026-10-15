import { createServer, IncomingMessage, ServerResponse } from "node:http";
import { createReadStream, existsSync, statSync } from "node:fs";
import { readFile, writeFile, unlink, readdir, mkdir } from "node:fs/promises";
import { join, extname, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

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
    const id = pathname.replace("/api/videos/", "");
    const jobPath = join(JOBS_DIR, `${id}.json`);
    try {
      if (existsSync(jobPath)) {
        await unlink(jobPath);
      }
      // Dọn tệp video liên quan
      const possibleOutputs = [
        join(OUTPUT_DIR, "explainer", `${id}.mp4`),
        join(OUTPUT_DIR, "explainer", `${id}-thumb.png`),
        join(OUTPUT_DIR, "whiteboard", `${id}.mp4`),
        join(OUTPUT_DIR, "whiteboard", `${id}-sub.mp4`),
        join(OUTPUT_DIR, "whiteboard", `${id}-thumb.png`),
        join(OUTPUT_DIR, "whiteboard", `${id}-sub-thumb.png`),
      ];
      for (const p of possibleOutputs) {
        if (existsSync(p)) await unlink(p).catch(() => {});
      }
      sendJson(res, 200, { success: true, message: `Đã xóa thành công ${id}` });
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
