/**
 * OmniVideo Studio - Video Library SPA Client Logic
 * Handles Video Grid, Modal Players, CRUD operations & SSE Re-render Streaming
 */

let allVideos = [];
let currentFilter = "all";
let currentSearch = "";
let activeEventSource = null;

// DOM Elements
const videoGrid = document.getElementById("video-grid");
const searchInput = document.getElementById("search-input");
const filterTabs = document.querySelectorAll(".tab-btn");
const statTotalVideos = document.getElementById("stat-total-videos");
const statTotalSize = document.getElementById("stat-total-size");

// Modals
const playerModal = document.getElementById("player-modal");
const createModal = document.getElementById("create-modal");
const editModal = document.getElementById("edit-modal");
const renderModal = document.getElementById("render-modal");

// Player Elements
const mainVideo = document.getElementById("main-video");
const modalVideoTitle = document.getElementById("modal-video-title");
const modalWorkshopBadge = document.getElementById("modal-workshop-badge");
const beatsTimeline = document.getElementById("beats-timeline");
const beatsCountBadge = document.getElementById("beats-count-badge");
const btnDownloadMp4 = document.getElementById("btn-download-mp4");
const btnDownloadSrt = document.getElementById("btn-download-srt");
const btnDownloadJson = document.getElementById("btn-download-json");

// Render Terminal Elements
const renderTerminal = document.getElementById("render-terminal");
const renderProgressBar = document.getElementById("render-progress-bar");
const renderModalTitle = document.getElementById("render-modal-title");
const btnCloseRender = document.getElementById("btn-close-render");

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "0 MB";
  const mb = bytes / (1024 * 1024);
  return mb.toFixed(2) + " MB";
}

async function loadVideos() {
  try {
    const res = await fetch("/api/videos");
    const data = await res.json();
    if (data.success) {
      allVideos = data.videos;
      updateStats();
      renderGrid();
    }
  } catch (err) {
    console.error("Loi khi tai danh sach video:", err);
    videoGrid.innerHTML = `<div class="error-state">Khong the ket noi den server: ${err.message}</div>`;
  }
}

function updateStats() {
  statTotalVideos.textContent = allVideos.length;
  const totalBytes = allVideos.reduce((acc, v) => acc + (v.sizeBytes || 0), 0);
  statTotalSize.textContent = formatBytes(totalBytes);
}

function renderGrid() {
  const filtered = allVideos.filter(v => {
    const matchesWorkshop = currentFilter === "all" || v.workshop === currentFilter;
    const term = currentSearch.toLowerCase();
    const matchesSearch = !term || 
      v.title.toLowerCase().includes(term) || 
      v.id.toLowerCase().includes(term) ||
      (v.beats && v.beats.some(b => b.rawText?.toLowerCase().includes(term)));
    return matchesWorkshop && matchesSearch;
  });

  if (filtered.length === 0) {
    videoGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
        <p style="font-size: 32px; margin-bottom: 12px;">📭</p>
        <p style="font-size: 16px; font-weight: 600;">Chưa có video nào phù hợp</p>
        <p style="font-size: 13px; margin-top: 6px;">Bấm nút "+ Tạo Video Mới" ở góc phải để bắt đầu sản xuất!</p>
      </div>
    `;
    return;
  }

  videoGrid.innerHTML = filtered.map(v => {
    const isPortrait = v.canvas.height > v.canvas.width;
    const badgeClass = `badge-${v.workshop}`;
    const workshopName = v.workshop === "threads" ? "Xưởng 5 (Threads)" :
                         v.workshop === "cinematic" ? "Xưởng 4 (Phim 3D)" :
                         v.workshop === "whiteboard" ? "Xưởng 3 (Bảng Trắng)" :
                         v.workshop === "explainer" ? "Xưởng 2 (Explainer)" : "Xưởng 1 (Tin Tức)";

    return `
      <div class="video-card" data-id="${v.id}">
        <div class="card-thumb-wrap ${isPortrait ? 'portrait-preview' : ''}" onclick="openPlayer('${v.id}')">
          ${v.thumbUrl 
            ? `<img class="card-thumb-img" src="${v.thumbUrl}" alt="${v.title}">` 
            : `<div class="card-thumb-placeholder">🎬</div>`}
          
          <span class="badge-tag ${badgeClass}">${v.workshop}</span>
          ${v.sizeBytes ? `<span class="badge-duration">${formatBytes(v.sizeBytes)}</span>` : ''}

          <div class="thumb-overlay">
            <div class="play-circle">▶</div>
          </div>
        </div>

        <div class="card-body">
          <h3 class="card-title" title="${v.title}">${v.title}</h3>
          
          <div class="card-meta">
            <span>⏱️ ${v.beatsCount} beats</span>
            <span>🎙️ ${v.voice?.voiceId ? v.voice.voiceId.replace('vi-VN-', '') : 'NamMinh'}</span>
            <span>📐 ${v.canvas.width}x${v.canvas.height}</span>
          </div>

          <div class="card-actions">
            <div class="btn-icon-group">
              <button class="btn btn-sm btn-primary" onclick="openPlayer('${v.id}')" title="Xem Video">
                ▶ Phát
              </button>
              <button class="btn btn-sm btn-outline" onclick="openEditor('${v.id}')" title="Sửa Kịch Bản">
                ✏️ Sửa
              </button>
              <button class="btn btn-sm btn-outline" onclick="triggerRender('${v.id}')" title="Re-render">
                ⚡ Render
              </button>
            </div>

            <button class="btn btn-sm btn-danger" onclick="deleteVideo('${v.id}')" title="Xóa">
              🗑️
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// ── PLAY VIDEO MODAL ──
function openPlayer(jobId) {
  const video = allVideos.find(v => v.id === jobId);
  if (!video) return;

  modalVideoTitle.textContent = video.title;
  modalWorkshopBadge.textContent = video.workshop.toUpperCase();
  modalWorkshopBadge.className = `badge badge-${video.workshop}`;
  beatsCountBadge.textContent = `${video.beatsCount} beats`;

  if (video.videoUrl) {
    mainVideo.src = video.videoUrl;
    mainVideo.load();
    btnDownloadMp4.href = video.videoUrl;
    btnDownloadMp4.style.display = "inline-flex";
  } else {
    mainVideo.src = "";
    btnDownloadMp4.style.display = "none";
  }

  btnDownloadJson.href = `/api/videos/${encodeURIComponent(jobId)}`;
  btnDownloadJson.setAttribute("download", `${jobId}.json`);

  if (video.srtUrl) {
    btnDownloadSrt.href = video.srtUrl;
    btnDownloadSrt.style.display = "inline-flex";
  } else {
    btnDownloadSrt.style.display = "none";
  }

  // Render Beats Timeline
  beatsTimeline.innerHTML = (video.beats || []).map((beat, idx) => {
    return `
      <div class="beat-item" onclick="seekVideoBeat(${idx})">
        <div class="beat-header">
          <span class="beat-role-tag">${beat.role || 'beat'}</span>
          <span class="beat-speaker">${beat.voice?.speaker || `Nhịp ${idx + 1}`}</span>
        </div>
        <div class="beat-text">${beat.rawText}</div>
      </div>
    `;
  }).join("");

  playerModal.classList.add("active");
}

function seekVideoBeat(index) {
  if (mainVideo.duration && allVideos.length) {
    const activeCard = beatsTimeline.querySelectorAll(".beat-item");
    activeCard.forEach((c, i) => c.classList.toggle("active", i === index));
    // Chia đều thời gian theo beat
    const timePerBeat = mainVideo.duration / Math.max(1, activeCard.length);
    mainVideo.currentTime = index * timePerBeat;
    mainVideo.play();
  }
}

// ── CREATE JOB MODAL ──
const createForm = document.getElementById("create-job-form");
document.getElementById("btn-open-create").onclick = () => {
  createModal.classList.add("active");
};
document.getElementById("btn-close-create").onclick = () => {
  createModal.classList.remove("active");
};
document.getElementById("btn-cancel-create").onclick = () => {
  createModal.classList.remove("active");
};

createForm.onsubmit = async (e) => {
  e.preventDefault();
  const id = document.getElementById("new-job-id").value.trim();
  const title = document.getElementById("new-title").value.trim();
  const workshop = document.getElementById("new-workshop").value;
  const archetype = document.getElementById("new-archetype").value;
  const voiceId = document.getElementById("new-voice").value;
  const platform = document.getElementById("new-platform").value;
  const rawScript = document.getElementById("new-raw-script").value.trim();

  const lines = rawScript ? rawScript.split("\n").filter(l => l.trim()) : [];
  const beats = lines.map((line, idx) => ({
    id: `beat_${String(idx + 1).padStart(2, "0")}`,
    role: idx === 0 ? "hook" : idx === lines.length - 1 ? "cta" : "story",
    rawText: line.trim(),
    visual: { headline: line.trim().slice(0, 40) }
  }));

  const defaultFps = (workshop === "explainer" || workshop === "whiteboard") ? 90 : 60;
  const canvas = platform === "tiktok"
    ? { width: 1080, height: 1920, fps: defaultFps }
    : { width: 1920, height: 1080, fps: defaultFps };

  const payload = {
    jobId: id,
    title,
    workshop,
    archetype,
    targetPlatform: platform,
    canvas,
    voice: { voiceId, speed: 1.0, rate: "+0%" },
    beats: beats.length ? beats : [
      { id: "beat_01", role: "hook", rawText: title, visual: { headline: title } }
    ],
  };

  try {
    const res = await fetch("/api/videos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.success) {
      createModal.classList.remove("active");
      createForm.reset();
      await loadVideos();
      if (confirm("Kịch bản đã tạo thành công! Bạn có muốn render video ngay bây giờ không?")) {
        triggerRender(id);
      }
    } else {
      alert("Lỗi: " + result.error);
    }
  } catch (err) {
    alert("Không thể lưu: " + err.message);
  }
};

// ── EDIT JOB MODAL ──
async function openEditor(jobId) {
  const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`);
  const data = await res.json();
  if (!data.success) {
    alert("Không tìm thấy kịch bản!");
    return;
  }

  const job = data.job;
  document.getElementById("edit-job-id").value = job.jobId;
  document.getElementById("edit-title").value = job.title;

  const container = document.getElementById("edit-beats-container");
  container.innerHTML = (job.beats || []).map((beat, idx) => {
    return `
      <div class="beat-edit-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); padding: 14px; border-radius: var(--radius-md); margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-size: 12px; font-weight: 700; color: var(--primary);">Beat ${idx + 1} (${beat.role})</span>
          <input type="text" class="beat-speaker-input" value="${beat.voice?.speaker || ''}" placeholder="Tên nhân vật / vai" style="width: 140px; font-size: 11px; padding: 4px 8px;">
        </div>
        <textarea class="beat-raw-text" rows="2" style="width: 100%;">${beat.rawText}</textarea>
      </div>
    `;
  }).join("");

  editModal.classList.add("active");
}

document.getElementById("btn-close-edit").onclick = () => editModal.classList.remove("active");
document.getElementById("btn-cancel-edit").onclick = () => editModal.classList.remove("active");

document.getElementById("edit-job-form").onsubmit = async (e) => {
  e.preventDefault();
  await saveEditJob(false);
};

document.getElementById("btn-save-and-render").onclick = async () => {
  await saveEditJob(true);
};

async function saveEditJob(andRender = false) {
  const jobId = document.getElementById("edit-job-id").value;
  const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`);
  const data = await res.json();
  const job = data.job;

  job.title = document.getElementById("edit-title").value;
  const textareas = document.querySelectorAll(".beat-raw-text");
  const speakerInputs = document.querySelectorAll(".beat-speaker-input");

  job.beats.forEach((b, idx) => {
    if (textareas[idx]) b.rawText = textareas[idx].value.trim();
    if (speakerInputs[idx]) {
      if (!b.voice) b.voice = {};
      b.voice.speaker = speakerInputs[idx].value.trim() || undefined;
    }
  });

  const saveRes = await fetch(`/api/videos/${encodeURIComponent(jobId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job)
  });

  if (saveRes.ok) {
    editModal.classList.remove("active");
    await loadVideos();
    if (andRender) {
      triggerRender(jobId);
    }
  } else {
    alert("Lưu thất bại!");
  }
}

// ── DELETE VIDEO ──
async function deleteVideo(jobId) {
  if (confirm(`Bạn có chắc chắn muốn xóa video '${jobId}' và kịch bản không?`)) {
    try {
      const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`, { method: "DELETE" });
      if (res.ok) {
        await loadVideos();
      } else {
        alert("Lỗi khi xóa!");
      }
    } catch (e) {
      alert("Lỗi kết nối: " + e.message);
    }
  }
}

// ── RE-RENDER WITH SSE STREAMING ──
function triggerRender(jobId) {
  if (activeEventSource) {
    activeEventSource.close();
  }

  renderTerminal.innerHTML = `<div class="terminal-line">[SYSTEM] Khởi động render cho ${jobId}...</div>`;
  renderModalTitle.textContent = `Đang render: ${jobId}`;
  btnCloseRender.disabled = true;
  renderModal.classList.add("active");

  const encId = encodeURIComponent(jobId);
  activeEventSource = new EventSource(`/api/render/${encId}`);

  activeEventSource.addEventListener("log", (e) => {
    try {
      const data = JSON.parse(e.data);
      appendLog(data.text);
    } catch (_) {
      appendLog(e.data);
    }
  });

  activeEventSource.addEventListener("progress", (e) => {
    try {
      const data = JSON.parse(e.data);
      appendLog(data.text);
    } catch (_) {
      appendLog(e.data);
    }
  });

  activeEventSource.addEventListener("error", (e) => {
    let msg = "";
    if (e.data) {
      try {
        const data = JSON.parse(e.data);
        msg = data.text || e.data;
      } catch (_) {
        msg = e.data;
      }
    }
    if (msg) {
      appendLog(`[ERROR] ${msg}`, "error");
      btnCloseRender.disabled = false;
      activeEventSource.close();
    }
  });

  activeEventSource.onerror = () => {
    if (activeEventSource.readyState === EventSource.CLOSED) {
      btnCloseRender.disabled = false;
    } else if (activeEventSource.readyState === EventSource.CONNECTING) {
      appendLog("[ERROR] Mất kết nối tới máy chủ render.", "error");
      btnCloseRender.disabled = false;
      activeEventSource.close();
    }
  };

  activeEventSource.addEventListener("done", (e) => {
    try {
      const data = JSON.parse(e.data);
      appendLog(`[SUCCESS] ${data.message}`, "done");
    } catch (_) {
      appendLog(`[SUCCESS] Hoàn thành!`, "done");
    }
    btnCloseRender.disabled = false;
    activeEventSource.close();
    loadVideos();
  });
}

function appendLog(text, type = "normal") {
  const line = document.createElement("div");
  line.className = `terminal-line ${type}`;
  line.textContent = text;
  renderTerminal.appendChild(line);
  renderTerminal.scrollTop = renderTerminal.scrollHeight;
}

btnCloseRender.onclick = () => renderModal.classList.remove("active");
document.getElementById("btn-close-player").onclick = () => {
  playerModal.classList.remove("active");
  mainVideo.pause();
};

// ── EVENT LISTENERS (Filter & Search) ──
searchInput.oninput = (e) => {
  currentSearch = e.target.value;
  renderGrid();
};

filterTabs.forEach(tab => {
  tab.onclick = () => {
    filterTabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    currentFilter = tab.dataset.workshop;
    renderGrid();
  };
});

// Init load
loadVideos();

// ========================================================
// ⚡ ANTIGRAVITY 2.0 LIVE BRIDGE & MISSION CONTROL CLIENT
// ========================================================

let antigravityEventSource = null;
let liveAntigravityEvents = [];
let currentTerminalFilter = "all";
let currentGate = 6;

const antigravityTerminal = document.getElementById("antigravity-live-terminal");
const terminalStepIndicator = document.getElementById("terminal-step-indicator");
const terminalMtimeIndicator = document.getElementById("terminal-mtime-indicator");
const missionConvoId = document.getElementById("mission-convo-id");
const missionStatusText = document.getElementById("mission-status-text");
const missionStatusDot = document.getElementById("mission-status-dot");
const antigravityText = document.getElementById("antigravity-text");
const antigravityGateBadge = document.getElementById("antigravity-gate-badge");
const dispatchForm = document.getElementById("antigravity-dispatch-form");
const dispatchFeedback = document.getElementById("dispatch-feedback");
const gateOverallProgress = document.getElementById("gate-overall-progress");

function updateGateStepper(gateNumber, gateName, progressPercent = 75) {
  currentGate = gateNumber;
  if (antigravityGateBadge) antigravityGateBadge.textContent = `Cổng ${gateNumber}`;
  if (gateOverallProgress) {
    const overall = Math.min(100, Math.round(((gateNumber - 1) * 100 + progressPercent) / 7));
    gateOverallProgress.textContent = `Tiến độ: ${overall}% (Cổng ${gateNumber}/7: ${gateName})`;
  }

  for (let i = 1; i <= 7; i++) {
    const card = document.getElementById(`gate-card-${i}`);
    const icon = document.getElementById(`gate-icon-${i}`);
    const bar = document.getElementById(`gate-bar-${i}`);
    if (!card || !bar) continue;

    card.className = "gate-card p-2.5 rounded-xl border flex flex-col gap-1.5 transition-all ";

    if (i < gateNumber) {
      // Completed gate
      card.className += "border-primary/50 bg-surface-container-lowest/90 gate-done";
      if (icon) {
        icon.className = "material-symbols-outlined text-[14px] text-primary";
        icon.textContent = "check_circle";
      }
      bar.className = "bg-primary h-full rounded-full w-full";
      bar.style.width = "100%";
    } else if (i === gateNumber) {
      // Active running gate
      card.className += "border-2 border-secondary bg-surface-container-lowest/95 gate-active";
      if (icon) {
        icon.className = "w-2 h-2 rounded-full bg-secondary animate-ping";
        icon.textContent = "";
      }
      bar.className = "bg-secondary h-full rounded-full";
      bar.style.width = `${progressPercent}%`;
    } else {
      // Pending gate
      card.className += "border-outline-variant/30 bg-surface-container-lowest/60";
      if (icon) {
        icon.className = "material-symbols-outlined text-[14px] text-outline";
        icon.textContent = "radio_button_unchecked";
      }
      bar.className = "bg-outline h-full rounded-full";
      bar.style.width = "0%";
    }
  }
}

function appendTerminalLine(text, type = "normal", category = "other") {
  const line = document.createElement("div");
  line.className = `terminal-line ${type}`;
  line.dataset.category = category;
  line.innerHTML = text;

  // Filter check
  if (currentTerminalFilter !== "all" && currentTerminalFilter !== category) {
    line.style.display = "none";
  }

  antigravityTerminal.appendChild(line);
  antigravityTerminal.scrollTop = antigravityTerminal.scrollHeight;
}

function formatEventTimestamp(isoStr) {
  if (!isoStr) return new Date().toLocaleTimeString("vi-VN");
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString("vi-VN", { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (_) {
    return "";
  }
}

function processIncomingEvent(ev) {
  liveAntigravityEvents.push(ev);
  const time = formatEventTimestamp(ev.timestamp);

  // Cập nhật Cổng quy trình nếu có
  const gateObj = ev.gate || ev.gateProgress;
  if (gateObj) {
    const gNum = gateObj.gateNumber || gateObj.gate || 1;
    const gName = gateObj.gateName || gateObj.name || `Cổng ${gNum}`;
    const gProg = gateObj.progressPercent || gateObj.progress || 50;
    updateGateStepper(gNum, gName, gProg);
    appendTerminalLine(
      `<span class="text-secondary">[${time}]</span> <span class="text-amber-300 font-bold">[GATE ${gNum}]</span> ${escapeHtml(gName)} (${gProg}%)`,
      "gate",
      "gate"
    );
  }

  // 1. Thinking / Suy nghĩ nội tâm của Agent
  if (ev.thought) {
    const preview = ev.thought.length > 280 ? ev.thought.slice(0, 280) + "..." : ev.thought;
    appendTerminalLine(
      `<span class="text-outline">[${time}]</span> <span class="text-cyan-400 font-semibold">[THOUGHT]</span> <span class="italic text-slate-300">${escapeHtml(preview)}</span>`,
      "thought",
      "thought"
    );
  }

  // 2. Tool Calls / Thực thi công cụ
  const toolList = ev.toolDetails || ev.toolCalls;
  if (toolList && toolList.length > 0) {
    for (const tool of toolList) {
      const toolName = typeof tool === "string" ? tool : (tool.name || "tool");
      const summary = typeof tool === "object" ? (tool.summary || tool.command || toolName) : tool;
      appendTerminalLine(
        `<span class="text-outline">[${time}]</span> <span class="text-emerald-400 font-bold">[TOOL]</span> <span class="text-primary font-mono">${escapeHtml(toolName)}</span>: <span class="text-on-surface-variant font-mono text-[11px]">${escapeHtml(summary)}</span>`,
        "tool",
        "tool"
      );
    }
  }

  // 3. User Input / Prompt từ người dùng hoặc Dispatch Web
  if (ev.type === "USER_INPUT") {
    appendTerminalLine(
      `<span class="text-outline">[${time}]</span> <span class="text-purple-400 font-bold">[USER]</span> <span class="text-purple-200 font-semibold">${escapeHtml(ev.contentPreview || ev.preview || ev.content || "")}</span>`,
      "user",
      "gate"
    );
  } else if (ev.type === "GENERIC" && ev.contentPreview) {
    // Kết quả ngắn từ lệnh chạy
    appendTerminalLine(
      `<span class="text-outline">[${time}]</span> <span class="text-slate-400 font-mono text-[11px]">[OUTPUT] ${escapeHtml(ev.contentPreview.slice(0, 140))}...</span>`,
      "normal",
      "tool"
    );
  }

  // Cập nhật chỉ số bước chân
  if (terminalStepIndicator && ev.stepIndex) {
    terminalStepIndicator.textContent = `Bước #${ev.stepIndex}: ${ev.type || 'Hoạt động'}`;
  }
  if (terminalMtimeIndicator) {
    terminalMtimeIndicator.textContent = `Cập nhật: ${time}`;
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function initAntigravityBridge() {
  if (antigravityEventSource) {
    antigravityEventSource.close();
  }

  try {
    antigravityEventSource = new EventSource("/api/antigravity/stream");

    antigravityEventSource.addEventListener("init", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.activeSession) {
          if (missionConvoId) missionConvoId.textContent = data.activeSession.slice(0, 12) + "...";
          if (antigravityText) antigravityText.textContent = "Antigravity 2.0: Kết Nối";
          if (missionStatusText) missionStatusText.textContent = "ĐỒNG BỘ HAI CHIỀU ANTIGRAVITY 2.0";
          if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-primary animate-pulse";
        }
      } catch (err) {
        console.warn("Lỗi xử lý init SSE:", err);
      }
    });

    antigravityEventSource.addEventListener("history", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.events && Array.isArray(data.events)) {
          antigravityTerminal.innerHTML = "";
          for (const ev of data.events) {
            processIncomingEvent(ev);
          }
        }
      } catch (err) {
        console.warn("Lỗi xử lý history SSE:", err);
      }
    });

    antigravityEventSource.addEventListener("step", (e) => {
      try {
        const ev = JSON.parse(e.data);
        processIncomingEvent(ev);
      } catch (err) {
        console.warn("Lỗi xử lý step SSE:", err);
      }
    });

    antigravityEventSource.addEventListener("status", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (!data.connected) {
          if (antigravityText) antigravityText.textContent = "Antigravity 2.0: Chờ";
          if (missionStatusText) missionStatusText.textContent = "ĐANG CHỜ TIẾN TRÌNH ANTIGRAVITY...";
          if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping";
        }
      } catch (_) {}
    });

    antigravityEventSource.onerror = () => {
      if (antigravityText) antigravityText.textContent = "Antigravity 2.0: Kết Nối Lại...";
      if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping";
    };
  } catch (err) {
    console.error("Không thể khởi tạo EventSource Antigravity:", err);
  }
}

// ── FAST GATE APPROVAL (HUMAN-IN-THE-LOOP) ──
window.quickApproveGate = async function(gateName) {
  try {
    appendTerminalLine(
      `<span class="text-amber-300 font-bold">[ACTION]</span> Đang gửi tín hiệu phê duyệt: <span class="text-white">${escapeHtml(gateName)}</span> vào IDE...`,
      "normal",
      "gate"
    );

    const res = await fetch("/api/antigravity/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gate: gateName }),
    });
    const result = await res.json();

    if (result.success) {
      appendTerminalLine(
        `<span class="text-emerald-400 font-bold">[SUCCESS]</span> Đã chuyển lệnh phê duyệt thành công vào Antigravity IDE! Agent đang tiếp tục tiến trình...`,
        "done",
        "gate"
      );
      // Advance gate stepper visually
      if (currentGate < 7) {
        updateGateStepper(currentGate + 1, "Đang xử lý sau phê duyệt", 30);
      }
    } else {
      appendTerminalLine(
        `<span class="text-rose-400 font-bold">[ERROR]</span> Không thể gửi phê duyệt: ${escapeHtml(result.error || "Lỗi không xác định")}`,
        "error",
        "gate"
      );
    }
  } catch (err) {
    appendTerminalLine(
      `<span class="text-rose-400 font-bold">[ERROR]</span> Lỗi kết nối: ${escapeHtml(err.message)}`,
      "error",
      "gate"
    );
  }
};

// ── TERMINAL FILTERS & CLEAR ──
window.clearLiveTerminal = function() {
  antigravityTerminal.innerHTML = `<div class="text-secondary/70">[SYSTEM] Đã xóa màn hình log terminal.</div>`;
};

document.querySelectorAll(".terminal-filter-btn").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll(".terminal-filter-btn").forEach(b => {
      b.classList.remove("active", "bg-secondary/20", "text-secondary");
      b.classList.add("text-outline");
    });
    btn.classList.add("active", "bg-secondary/20", "text-secondary");
    btn.classList.remove("text-outline");

    currentTerminalFilter = btn.dataset.filter;
    const lines = antigravityTerminal.querySelectorAll(".terminal-line");
    lines.forEach(line => {
      if (currentTerminalFilter === "all" || line.dataset.category === currentTerminalFilter) {
        line.style.display = "block";
      } else {
        line.style.display = "none";
      }
    });
  };
});

// ── DISPATCH FORM SUBMISSION (WEB -> IDE) ──
if (dispatchForm) {
  dispatchForm.onsubmit = async (e) => {
    e.preventDefault();
    const workshop = document.getElementById("dispatch-workshop").value;
    const topic = document.getElementById("dispatch-topic").value.trim();
    const bg = document.getElementById("dispatch-bg").value;
    const speed = document.getElementById("dispatch-speed").value;
    const publish = document.getElementById("dispatch-publish").checked;

    if (!topic) return;

    const btnSubmit = document.getElementById("btn-dispatch-antigravity");
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span class="spinner inline-block w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin"></span> <span>Đang Gửi Vào IDE...</span>`;

    // Chuẩn hóa prompt chỉ thị quy chuẩn cho Antigravity Agent
    let prompt = "";
    if (workshop === "threads") {
      prompt = `Hãy sản xuất video Threads cho bài viết: ${topic}. Áp dụng đầy đủ 10 Quy tắc Xưởng 5 (AGENTS.md): Dark Mode AMOLED (#101010) chiều rộng 820px, Avatar thật từ CDN, Voice x${speed} (Edge-TTS) lọc sạch icon và phiên âm ngữ âm tiếng Anh, Meme Sticker đồng bộ tại điểm punchline (không phát SFX ở đầu câu), Gameplay nền: ${bg}${publish ? ', và tự động đóng gói xuất bản YouTube Unlisted (Cổng 7)' : ''}.`;
    } else if (workshop === "cinematic") {
      prompt = `Hãy sản xuất tập phim điện ảnh 3D cho chủ đề: ${topic}. Tuân thủ nghiêm ngặt 14 Quy tắc Điện ảnh (AGENTS.md): Voice x${speed}, nhịp ASL 3.5s - 6s, 100% video AI GEN V chuyển động thực sự (cấm zoompan ảnh tĩnh), Cyber Chatbox overlay (1600x125px viền Cyan Neon), Fresh-Render không tái sử dụng asset cũ${publish ? ', và tự động đăng YouTube Unlisted (Cổng 7)' : ''}.`;
    } else if (workshop === "whiteboard") {
      prompt = `Hãy sản xuất video truyện dài bảng trắng cho chủ đề: ${topic}. Sử dụng Xưởng 3: OpenCV 90 FPS, Storyboard Notion Art độc quyền từng chương, lồng nhạc nền ducking thông minh${publish ? ', và đăng YouTube Unlisted' : ''}.`;
    } else if (workshop === "explainer") {
      prompt = `Hãy sản xuất video giải thích công nghệ bằng Remotion cho chủ đề: ${topic}. Cấu trúc 6-beat tâm lý học, chuyển động code React và sơ đồ trực quan.`;
    } else {
      prompt = `Hãy sản xuất video tin tức ngắn HyperFrames 9:16 cho chủ đề: ${topic}. Định dạng thời sự quốc tế, kinetic subtitles tự động.`;
    }

    try {
      appendTerminalLine(
        `<span class="text-secondary font-bold">[DISPATCH_WEB]</span> Gửi lệnh sản xuất: <span class="text-primary font-semibold">${escapeHtml(topic)}</span> (${workshop})`,
        "user",
        "gate"
      );

      const res = await fetch("/api/antigravity/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();

      dispatchFeedback.classList.remove("hidden");
      if (data.success) {
        dispatchFeedback.className = "mt-3 p-2.5 rounded-lg text-xs font-mono bg-primary/15 border border-primary/40 text-primary";
        dispatchFeedback.innerHTML = `✅ <strong>Đã gửi lệnh vào Antigravity IDE thành công!</strong><br/>Agent đang tiếp nhận chỉ thị và bắt đầu tiến trình sản xuất.`;
        updateGateStepper(1, "Ý Tưởng & Kịch Bản", 40);
        dispatchForm.reset();
      } else {
        dispatchFeedback.className = "mt-3 p-2.5 rounded-lg text-xs font-mono bg-rose-500/15 border border-rose-500/40 text-rose-300";
        dispatchFeedback.innerHTML = `❌ <strong>Lỗi:</strong> ${escapeHtml(data.error || "Không thể gửi lệnh")}`;
      }
    } catch (err) {
      dispatchFeedback.classList.remove("hidden");
      dispatchFeedback.className = "mt-3 p-2.5 rounded-lg text-xs font-mono bg-rose-500/15 border border-rose-500/40 text-rose-300";
      dispatchFeedback.innerHTML = `❌ <strong>Lỗi kết nối:</strong> ${escapeHtml(err.message)}`;
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `<span class="material-symbols-outlined text-[18px]">rocket_launch</span> <span>Gửi Lệnh Sản Xuất Vào Antigravity IDE</span>`;
      setTimeout(() => {
        dispatchFeedback.classList.add("hidden");
      }, 7000);
    }
  };
}

// Khởi chạy Antigravity Stream ngay khi tải trang
initAntigravityBridge();
