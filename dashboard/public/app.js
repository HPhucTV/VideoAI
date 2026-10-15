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
    const workshopName = v.workshop === "explainer" ? "Xưởng 2 (Explainer)" :
                         v.workshop === "whiteboard" ? "Xưởng 3 (Bảng Trắng)" : "Xưởng 1 (Tin Tức)";

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
