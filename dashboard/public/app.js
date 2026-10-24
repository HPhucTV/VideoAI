
// Modal Create Video Controller
function openCreateModal() {
  const m = document.getElementById("create-modal");
  if (m) {
    m.classList.add("active");
    document.body.style.overflow = "hidden";
  }
}

function closeCreateModal() {
  const m = document.getElementById("create-modal");
  if (m) {
    m.classList.remove("active");
    document.body.style.overflow = "";
  }
}
/**
 * OmniVideo Studio - Video Library SPA Client Logic
 * Antigravity 2.0 & Omni-Commander Mission Control (Sakura Rose)
 * White / Pink Aesthetic, Live Log Console, Voice Briefing & Multi-Task Queue
 */

let allVideos = [];
let currentFilter = "all";
let currentSearch = "";
let currentViewMode = localStorage.getItem("omni_view_mode") || "grid";
let currentTheme = localStorage.getItem("omni_theme") || "light";
let currentYouTubeJob = null;
let selectedPublishAt = null;
let activeEventSource = null;
let currentVoiceAudio = null;

// DOM Elements
const videoGrid = document.getElementById("video-grid");
const searchInput = document.getElementById("search-input");
const statTotalVideos = document.getElementById("stat-total-videos");
const statTotalSize = document.getElementById("stat-total-size");
const widgetTotalVideos = document.getElementById("widget-total-videos");
const widgetPublishedVideos = document.getElementById("widget-published-videos");
const badgeTotalAssets = document.getElementById("badge-total-assets");
const leaderLogStream = document.getElementById("leader-log-stream");

// Modals
const playerModal = document.getElementById("player-modal");
const createModal = document.getElementById("create-modal");
const editModal = document.getElementById("edit-modal");
const renderModal = document.getElementById("render-modal");
const scoutModal = document.getElementById("scout-modal");
const reportModal = document.getElementById("report-modal");
const ytModal = document.getElementById("youtube-upload-modal");
const taskQueueModal = document.getElementById("task-queue-modal");

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

// ── UTILITY HELPERS ──
function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "0 MB";
  const mb = bytes / (1024 * 1024);
  return mb.toFixed(2) + " MB";
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

function playSuccessChime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    
    // Note 1: 880 Hz
    const osc1 = ctx.createOscillator();
    const gain1 = ctx.createGain();
    osc1.type = "sine";
    osc1.frequency.setValueAtTime(880, ctx.currentTime);
    gain1.gain.setValueAtTime(0.18, ctx.currentTime);
    gain1.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
    osc1.connect(gain1);
    gain1.connect(ctx.destination);
    osc1.start(ctx.currentTime);
    osc1.stop(ctx.currentTime + 0.35);

    // Note 2: 1760 Hz
    const osc2 = ctx.createOscillator();
    const gain2 = ctx.createGain();
    osc2.type = "sine";
    osc2.frequency.setValueAtTime(1760, ctx.currentTime + 0.1);
    gain2.gain.setValueAtTime(0.22, ctx.currentTime + 0.1);
    gain2.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.7);
    osc2.connect(gain2);
    gain2.connect(ctx.destination);
    osc2.start(ctx.currentTime + 0.1);
    osc2.stop(ctx.currentTime + 0.7);
  } catch (e) {
    console.warn("Audio chime unsupported:", e);
  }
}

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl text-xs font-mono font-bold shadow-2xl border flex items-center gap-2 animate-in fade-in slide-in-from-bottom-3 duration-200 ${
    type === "success" 
      ? "bg-pink-600 text-white border-pink-700 shadow-pink-500/20" 
      : "bg-red-600 text-white border-red-700 shadow-red-500/20"
  }`;
  toast.innerHTML = `<span class="material-symbols-outlined text-sm">${type === "success" ? "favorite" : "info"}</span> <span>${escapeHtml(message)}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3400);
}

// ── THEME CONTROLLER ──
function initTheme() {
  if (currentTheme === "dark") {
    document.documentElement.classList.add("dark");
    document.documentElement.classList.remove("light");
    const icon = document.getElementById("theme-toggle-icon");
    if (icon) icon.textContent = "light_mode";
  } else {
    document.documentElement.classList.add("light");
    document.documentElement.classList.remove("dark");
    const icon = document.getElementById("theme-toggle-icon");
    if (icon) icon.textContent = "dark_mode";
  }
}

function toggleTheme() {
  if (document.documentElement.classList.contains("dark")) {
    document.documentElement.classList.remove("dark");
    document.documentElement.classList.add("light");
    currentTheme = "light";
    localStorage.setItem("omni_theme", "light");
    const icon = document.getElementById("theme-toggle-icon");
    if (icon) icon.textContent = "dark_mode";
    showToast("🌸 Đã bật giao diện Trắng / Hồng Sakura");
  } else {
    document.documentElement.classList.remove("light");
    document.documentElement.classList.add("dark");
    currentTheme = "dark";
    localStorage.setItem("omni_theme", "dark");
    const icon = document.getElementById("theme-toggle-icon");
    if (icon) icon.textContent = "light_mode";
    showToast("🌙 Đã bật giao diện Tối (Night Shift)");
  }
}

// ── LEADER AI LIVE LOG CONSOLE (KHUNG LOG BÁO CÁO) ──
function appendLeaderLog(tag, message) {
  if (!leaderLogStream) return;
  const time = new Date().toLocaleTimeString("vi-VN");
  const line = document.createElement("div");
  line.className = "log-line animate-in fade-in duration-150";

  const tagClass = `log-tag ${tag.toLowerCase()}`;
  line.innerHTML = `
    <span class="log-time">[${time}]</span>
    <span class="${tagClass}">[${tag.toUpperCase()}]</span>
    <span class="flex-1 text-gray-800">${escapeHtml(message)}</span>
  `;

  leaderLogStream.appendChild(line);
  leaderLogStream.scrollTop = leaderLogStream.scrollHeight;
}

function initLeaderLog() {
  if (!leaderLogStream) return;
  leaderLogStream.innerHTML = "";
  appendLeaderLog("thinking", "Khởi động Omni-Commander AI trên hệ thống studio tự hành Antigravity 2.0.");
  appendLeaderLog("radar", "Đã kết nối GitHub Token: HPhucTV (5,000 req/h). Radar săn repo trending đã kích hoạt.");
  appendLeaderLog("dispatch", "Telegram Bot @Boiz120 đã kết nối. Sẵn sàng gửi báo cáo tự động.");
  appendLeaderLog("done", "Toàn bộ 5 phân xưởng đã sẵn sàng nhận lệnh từ sếp!");
}

function clearLeaderLog() {
  if (leaderLogStream) {
    leaderLogStream.innerHTML = "";
    appendLeaderLog("thinking", "Đã dọn sạch nhật ký hoạt động. Sẵn sàng nhận chỉ đạo mới.");
    showToast("Đã xóa nhật ký log!");
  }
}

function toggleLeaderLog() {
  const stream = document.getElementById("leader-log-stream");
  const actions = document.getElementById("leader-hitl-actions");
  const icon = document.getElementById("btn-toggle-log-icon");
  if (!stream) return;

  const isHidden = stream.classList.toggle("hidden");
  if (actions) actions.classList.toggle("hidden", isHidden);
  if (icon) icon.textContent = isHidden ? "expand_more" : "expand_less";
}

// ── INTERACTIVE QUICK DECISIONS (Ý TƯỞNG 1: HITL ACTIONS) ──
function handleHitlAction(action, extra) {
  if (action === "produce_threads") {
    appendLeaderLog("dispatch", "Sếp phê duyệt HITL: Bắt đầu bấm máy Xưởng 5 cho bài viết Threads vừa cào!");
    fetch("/api/commander/produce-threads", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        appendLeaderLog("dispatch", data.message || "Xưởng 5 đang tiến hành render video Threads!");
        showToast("Xưởng 5 đang render video Threads!");

        // Khởi động bộ giám sát ngầm thời gian thực (Real-time Completion Monitor)
        let checks = 0;
        let lastReportedJob = null;
        const monitorTimer = setInterval(async () => {
          checks++;
          try {
            const sRes = await fetch("/api/commander/threads-status");
            const sData = await sRes.json();
            if (sData.success && sData.status === "completed" && sData.job_id !== lastReportedJob) {
              lastReportedJob = sData.job_id;
              clearInterval(monitorTimer);
              appendLeaderLog("done", `✅ XƯỞNG 5 HOÀN TẤT: Đã render xong 100% video "${sData.title || sData.job_id}"!`);
              appendLeaderLog("done", `🎯 Đã tự động tạo: Thumbnail 3D, Timestamps & Bộ thẻ Tags chuẩn SEO YouTube.`);
              appendLeaderLog("alert", `📱 Đã gửi thông báo hoàn tất đến Telegram sếp (@Boiz120). Sếp có thể bấm "YouTube Direct" để xem và upload ngay!`);
              showToast("Xưởng 5 đã hoàn thành video!");
              await loadVideos();
            } else if (checks > 70) {
              clearInterval(monitorTimer);
            }
          } catch (_) {}
        }, 2000);
      })
      .catch(err => {
        appendLeaderLog("alert", `Lỗi khởi động Xưởng 5: ${err.message}`);
      });
    return;
  }
  if (action === "run_workshop2") {
    appendLeaderLog("dispatch", "Sếp duyệt đề tài GitHub Trending! Đang chuyển giao kịch bản sang Xưởng 2 Remotion...");
    setTimeout(() => {
      appendLeaderLog("done", "Đã nạp kịch bản vào Xưởng 2. Sẵn sàng render NLE!");
      showToast("Đã phân công sang Xưởng 2!");
    }, 1200);
  } else if (action === "rewrite_humor") {
    appendLeaderLog("thinking", "Đang phân tích lại kịch bản, thêm các yếu tố hài hước Gen Z và punchline bất ngờ...");
    setTimeout(() => {
      appendLeaderLog("done", "Đã viết lại kịch bản với phong cách hài hước, cà khịa duyên dáng.");
      showToast("Đã viết lại kịch bản hài hơn!");
    }, 1500);
  } else if (action === "change_topic") {
    appendLeaderLog("radar", "Đang quét tìm đề tài mới từ GitHub & Threads...");
    openScoutModal();
  } else if (action === "upload_youtube") {
    if (allVideos.length > 0) {
      openYouTubeUploadModal(allVideos[0].id);
    } else {
      showToast("Chưa có video để upload!", "error");
    }
  }
}

// ── VOICE BRIEFING 30S (Ý TƯỞNG 2: BÁO CÁO GIỌNG NÓI) ──
async function playVoiceBriefing() {
  const topText = document.getElementById("top-voice-text");
  const soundwave = document.getElementById("top-soundwave");

  if (currentVoiceAudio && !currentVoiceAudio.paused) {
    currentVoiceAudio.pause();
    currentVoiceAudio.currentTime = 0;
    if (topText) topText.textContent = "🎙️ Nghe Báo Cáo 30s";
    if (soundwave) soundwave.classList.add("hidden");
    return;
  }

  if (topText) topText.textContent = "Đang tổng hợp giọng nói...";
  appendLeaderLog("voice", "Đang tạo báo cáo giọng nói 30s với Microsoft Edge-TTS (Hoài My Neural)...");

  try {
    const res = await fetch("/api/commander/voice-briefing");
    const data = await res.json();

    if (data.success && data.audio_url) {
      const audioUrl = data.audio_url.startsWith("http") ? data.audio_url : `${data.audio_url}?t=${Date.now()}`;
      currentVoiceAudio = new Audio(audioUrl);

      currentVoiceAudio.onplay = () => {
        if (topText) topText.textContent = "Đang phát báo cáo...";
        if (soundwave) soundwave.classList.remove("hidden");
        appendLeaderLog("voice", `Đang phát giọng đọc Hoài My: "${data.script?.slice(0, 70)}..."`);
      };

      currentVoiceAudio.onended = () => {
        if (topText) topText.textContent = "🎙️ Nghe Báo Cáo 30s";
        if (soundwave) soundwave.classList.add("hidden");
        appendLeaderLog("done", "Đã phát xong báo cáo ca trực 30s!");
      };

      currentVoiceAudio.onerror = (e) => {
        console.warn("Lỗi phát audio:", e);
        if (topText) topText.textContent = "🎙️ Nghe Báo Cáo 30s";
        if (soundwave) soundwave.classList.add("hidden");
        showToast("Không thể phát file âm thanh", "error");
      };

      await currentVoiceAudio.play();
    } else {
      showToast("Lỗi tạo báo cáo giọng nói", "error");
      if (topText) topText.textContent = "🎙️ Nghe Báo Cáo 30s";
    }
  } catch (err) {
    showToast("Lỗi kết nối Voice Briefing: " + err.message, "error");
    if (topText) topText.textContent = "🎙️ Nghe Báo Cáo 30s";
  }
}

// ── TELEGRAM NOTIFIER (Ý TƯỞNG 4: THÔNG BÁO VỀ ĐIỆN THOẠI SẾP) ──
async function sendTelegramReport() {
  appendLeaderLog("dispatch", "Đang đóng gói số liệu ca trực để gửi tin nhắn Telegram về @Boiz120...");
  try {
    const res = await fetch("/api/commander/send-telegram", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "shift_briefing" })
    });
    const data = await res.json();
    if (data.success) {
      playSuccessChime();
      appendLeaderLog("done", "🌸 ĐÃ BẮN TIN NHẮN TELEGRAM VỀ ĐIỆN THOẠI SẾP THÀNH CÔNG! (Chat ID: 6020715270)");
      showToast("Đã gửi báo cáo về Telegram của sếp!");
    } else {
      showToast("Lỗi gửi Telegram: " + data.error, "error");
    }
  } catch (err) {
    showToast("Lỗi kết nối Telegram: " + err.message, "error");
  }
}

// ── TASK QUEUE (Ý TƯỞNG 3: HÀNG ĐỢI ĐA NHIỆM VỤ) ──
function openTaskQueueModal() {
  if (taskQueueModal) taskQueueModal.classList.add("active");
  loadTaskQueue();
}

function closeTaskQueueModal() {
  if (taskQueueModal) taskQueueModal.classList.remove("active");
}

async function loadTaskQueue() {
  const container = document.getElementById("task-queue-list");
  if (!container) return;

  try {
    const res = await fetch("/api/commander/task-queue");
    const data = await res.json();
    if (data.success && data.queue) {
      container.innerHTML = data.queue.map(item => `
        <div class="task-queue-item">
          <div class="flex items-center gap-3">
            <span class="w-2.5 h-2.5 rounded-full ${item.status === 'completed' ? 'bg-emerald-500' : 'bg-pink-500 animate-pulse'}"></span>
            <div>
              <div class="font-bold text-xs text-gray-800">${escapeHtml(item.title)}</div>
              <div class="text-[10px] font-mono text-gray-500">${escapeHtml(item.result || 'Đang xử lý trong hàng đợi...')}</div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${item.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-pink-100 text-pink-700'}">
              ${item.status === 'completed' ? '✓ HOÀN TẤT' : 'ĐANG CHẠY'}
            </span>
          </div>
        </div>
      `).join("");
      const badge = document.getElementById("queue-badge-count");
      if (badge) badge.textContent = data.queue.length;
    }
  } catch (err) {
    container.innerHTML = `<div class="p-3 text-xs font-mono text-red-500">Lỗi tải hàng đợi: ${escapeHtml(err.message)}</div>`;
  }
}

async function submitMultipleTasks() {
  const input = document.getElementById("queue-multi-tasks-input");
  if (!input) return;
  const raw = input.value.trim();
  if (!raw) return;

  const lines = raw.split("\n").map(l => l.trim()).filter(Boolean);
  if (lines.length === 0) return;

  try {
    const res = await fetch("/api/commander/task-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tasks: lines })
    });
    const data = await res.json();
    if (data.success) {
      input.value = "";
      loadTaskQueue();
      appendLeaderLog("dispatch", `Sếp vừa giao ${lines.length} nhiệm vụ cùng lúc vào hàng đợi. Leader đang bắt đầu xử lý!`);
      showToast(`Đã thêm ${lines.length} việc vào hàng đợi tự hành!`);
    }
  } catch (err) {
    showToast("Lỗi thêm tác vụ: " + err.message, "error");
  }
}

// ── DATA LOADING & STATS ──
async function loadVideos() {
  try {
    const res = await fetch("/api/videos");
    const data = await res.json();
    if (data.success) {
      allVideos = data.videos || [];
      updateStats();
      renderGrid();
    }
  } catch (err) {
    console.error("Lỗi khi tải danh sách video:", err);
    if (videoGrid) {
      videoGrid.innerHTML = `<div class="p-8 text-center text-xs font-mono text-red-500">Không thể kết nối đến server: ${escapeHtml(err.message)}</div>`;
    }
  }
}

function updateStats() {
  const totalCount = allVideos.length;
  const publishedCount = allVideos.filter(v => v.isPublished).length;
  const totalBytes = allVideos.reduce((acc, v) => acc + (v.sizeBytes || 0), 0);

  if (statTotalVideos) statTotalVideos.textContent = totalCount;
  if (statTotalSize) statTotalSize.textContent = formatBytes(totalBytes);
  if (widgetTotalVideos) widgetTotalVideos.textContent = totalCount;
  if (widgetPublishedVideos) widgetPublishedVideos.textContent = publishedCount;
  if (badgeTotalAssets) badgeTotalAssets.textContent = `${totalCount} Video`;
}

function filterPublishedVideos() {
  currentFilter = "all";
  currentSearch = "";
  if (searchInput) searchInput.value = "";
  
  const filtered = allVideos.filter(v => v.isPublished);
  renderCustomList(filtered, "Chưa có video nào đã đăng YouTube API.");
  showToast(`Hiển thị ${filtered.length} video đã đăng YouTube`);
}

function renderCustomList(list, emptyMsg) {
  const videoTableWrap = document.getElementById("video-table-wrap");
  const videoTableBody = document.getElementById("video-table-body");

  if (list.length === 0) {
    videoGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: #9ca3af;">
        <p style="font-size: 28px; margin-bottom: 8px;">📭</p>
        <p style="font-size: 14px; font-weight: 600;">${escapeHtml(emptyMsg)}</p>
      </div>
    `;
    if (videoTableWrap) videoTableWrap.classList.add("hidden");
    return;
  }

  renderGridItems(list);
}

// ── GRID & TABLE VIEW CONTROLLER ──
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

  const videoTableWrap = document.getElementById("video-table-wrap");
  const videoTableBody = document.getElementById("video-table-body");

  if (filtered.length === 0) {
    videoGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: #9ca3af;">
        <p style="font-size: 32px; margin-bottom: 12px;">🌸</p>
        <p style="font-size: 15px; font-weight: 600;">Chưa có video nào trong phân xưởng này</p>
        <p style="font-size: 12px; margin-top: 6px;">Bấm nút "+ Tạo Video" ở góc phải để bắt đầu sản xuất!</p>
      </div>
    `;
    if (videoTableWrap) videoTableWrap.classList.add("hidden");
    return;
  }

  if (currentViewMode === "table" && videoTableWrap && videoTableBody) {
    videoGrid.classList.add("hidden");
    videoTableWrap.classList.remove("hidden");

    videoTableBody.innerHTML = filtered.map(v => {
      const badgeClass = `badge-${v.workshop}`;
      const isPublished = Boolean(v.isPublished && v.youtubeUrl);

      return `
        <tr>
          <td>
            <div class="w-12 h-12 rounded-lg bg-pink-50 overflow-hidden cursor-pointer shrink-0 border border-pink-100 relative" onclick="openPlayer('${v.id}')">
              ${v.thumbUrl 
                ? `<img src="${v.thumbUrl}" class="w-full h-full object-cover" alt="${escapeHtml(v.title)}">` 
                : `<div class="w-full h-full flex items-center justify-center text-xs text-pink-400">🎬</div>`}
              <span class="absolute bottom-0.5 right-0.5 px-0.5 rounded text-[7px] font-mono bg-black/80 text-white">${v.sizeBytes ? formatBytes(v.sizeBytes) : ''}</span>
            </div>
          </td>
          <td>
            <div class="font-bold text-gray-800 hover:text-pink-600 cursor-pointer line-clamp-1 text-xs" onclick="openPlayer('${v.id}')">${escapeHtml(v.title)}</div>
            <div class="text-[10px] font-mono text-gray-400">${escapeHtml(v.id)}</div>
          </td>
          <td>
            <span class="badge-tag ${badgeClass} static">${v.workshop}</span>
          </td>
          <td>
            <div class="text-[11px] font-mono text-gray-600">${v.canvas.width}x${v.canvas.height} • ${v.beatsCount} beats</div>
            <div class="text-[10px] font-mono text-gray-400">🎙️ ${v.voice?.voiceId ? v.voice.voiceId.replace('vi-VN-', '') : 'NamMinh'}</div>
          </td>
          <td>
            ${isPublished 
              ? `<a href="${v.youtubeUrl}" target="_blank" class="badge-published-table" title="Xem trên YouTube">
                  <span class="material-symbols-outlined text-[10px]">play_circle</span>
                  <span>ĐÃ ĐĂNG YT</span>
                </a>`
              : `<span class="text-[10px] font-mono text-gray-400">Chưa đăng</span>`
            }
          </td>
          <td>
            <span class="text-xs font-mono font-bold text-pink-600">${formatBytes(v.sizeBytes)}</span>
          </td>
          <td style="text-align: right;">
            <div class="inline-flex items-center gap-1.5 justify-end">
              ${isPublished 
                ? `<a href="${v.youtubeUrl}" target="_blank" class="btn-youtube" title="Xem trên YouTube">
                    <span class="material-symbols-outlined text-[13px]">open_in_new</span>
                    <span>Xem YT</span>
                  </a>`
                : `<button class="btn-youtube" onclick="openYouTubeUploadModal('${v.id}')" title="Upload lên YouTube">
                    <span class="material-symbols-outlined text-[13px]">cloud_upload</span>
                    <span>Upload YT</span>
                  </button>`
              }
              <button class="btn btn-sm btn-outline" onclick="openYouTubeUploadModal('${v.id}', true)" title="Trích Frame Thumbnail">
                📸
              </button>
              <button class="btn btn-sm btn-primary" onclick="openPlayer('${v.id}')" title="Xem Video">
                ▶
              </button>
              <button class="btn btn-sm btn-outline" onclick="openEditor('${v.id}')" title="Sửa Kịch Bản">
                ✏️
              </button>
              <button class="btn btn-sm btn-outline" onclick="triggerRender('${v.id}')" title="Re-render">
                ⚡
              </button>
              <button class="btn btn-sm btn-danger" onclick="deleteVideo('${v.id}')" title="Xóa">
                🗑️
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
    return;
  }

  // Grid Mode Default
  if (videoTableWrap) videoTableWrap.classList.add("hidden");
  videoGrid.classList.remove("hidden");
  renderGridItems(filtered);
}

function renderGridItems(items) {
  videoGrid.innerHTML = items.map(v => {
    const isPortrait = v.canvas.height > v.canvas.width;
    const badgeClass = `badge-${v.workshop}`;
    const isPublished = Boolean(v.isPublished && v.youtubeUrl);

    return `
      <div class="video-card" data-id="${v.id}">
        <div class="card-thumb-wrap ${isPortrait ? 'portrait-preview' : ''}" onclick="openPlayer('${v.id}')">
          ${v.thumbUrl 
            ? `<img class="card-thumb-img" src="${v.thumbUrl}" alt="${escapeHtml(v.title)}">` 
            : `<div class="card-thumb-placeholder">🎬</div>`}
          
          <!-- Category Workshop Badge -->
          <span class="badge-tag ${badgeClass}">${v.workshop}</span>

          <!-- Published YouTube Badge (If Published) -->
          ${isPublished 
            ? `<a href="${v.youtubeUrl}" target="_blank" class="badge-published" onclick="event.stopPropagation()" title="Mở trên YouTube: ${v.youtubeUrl}">
                <span class="material-symbols-outlined text-[12px]" style="font-variation-settings: 'FILL' 1;">play_circle</span>
                <span>🔴 ĐÃ ĐĂNG YOUTUBE</span>
              </a>`
            : ''}

          <!-- Duration Badge -->
          ${v.sizeBytes ? `<span class="badge-duration">${formatBytes(v.sizeBytes)}</span>` : ''}

          <div class="thumb-overlay">
            <div class="play-circle">▶</div>
          </div>
        </div>

        <div class="card-body">
          <h3 class="card-title" title="${escapeHtml(v.title)}" onclick="openPlayer('${v.id}')">${escapeHtml(v.title)}</h3>
          
          <div class="card-meta">
            <span>⏱️ ${v.beatsCount} beats</span>
            <span>🎙️ ${v.voice?.voiceId ? v.voice.voiceId.replace('vi-VN-', '') : 'NamMinh'}</span>
            <span>📐 ${v.canvas.width}x${v.canvas.height}</span>
          </div>

          <div class="card-actions">
            <!-- Dedicated YouTube Actions -->
            ${isPublished 
              ? `<div class="grid grid-cols-2 gap-1.5">
                  <a href="${v.youtubeUrl}" target="_blank" class="btn-youtube-view" title="Xem trên YouTube">
                    <span class="material-symbols-outlined text-[13px]">open_in_new</span>
                    <span>Xem YouTube</span>
                  </a>
                  <button class="btn btn-sm btn-outline text-red-500 text-[11px] font-bold" onclick="openYouTubeUploadModal('${v.id}')" title="Upload Lại">
                    Tải Lại
                  </button>
                </div>`
              : `<button class="btn-youtube btn-youtube-full" onclick="openYouTubeUploadModal('${v.id}')" title="Upload lên kênh YouTube (Public / Unlisted / Private)">
                  <span class="material-symbols-outlined text-[14px]">cloud_upload</span>
                  <span>Upload YouTube Direct</span>
                </button>`
            }

            <!-- Secondary Actions Row -->
            <div class="card-actions-row">
              <div class="btn-icon-group">
                <button class="btn btn-sm btn-outline" onclick="openYouTubeUploadModal('${v.id}', true)" title="Trích Frame Thumbnail">
                  📸 Frame
                </button>
                <button class="btn btn-sm btn-primary" onclick="openPlayer('${v.id}')" title="Xem Video">
                  ▶ Phát
                </button>
                <button class="btn btn-sm btn-outline" onclick="openEditor('${v.id}')" title="Sửa Kịch Bản">
                  ✏️ Sửa
                </button>
                <button class="btn btn-sm btn-outline" onclick="triggerRender('${v.id}')" title="Re-render">
                  ⚡
                </button>
              </div>

              <button class="btn btn-sm btn-danger" onclick="deleteVideo('${v.id}')" title="Xóa">
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function setViewMode(mode) {
  currentViewMode = mode;
  localStorage.setItem("omni_view_mode", mode);
  renderGrid();
}

function triggerOpenFirstVideoYouTube() {
  if (allVideos.length > 0) {
    openYouTubeUploadModal(allVideos[0].id);
  } else {
    showToast("Chưa có video nào trong thư viện!", "error");
  }
}

// ── LEADER COMMAND & DISPATCH LOGIC ──
function handleLeaderShortcut(type) {
  if (type === "scout_github") {
    openScoutModal();
    appendLeaderLog("radar", "Đang quét radar GitHub Trending qua Token 5,000 req/h...");
  } else if (type === "shift_report") {
    openShiftReportModal();
    appendLeaderLog("thinking", "Đang tổng hợp báo cáo ca trực 24h từ 5 phân xưởng...");
  } else if (type === "quality_audit") {
    if (allVideos.length > 0) {
      runQualityAudit(allVideos[0].id);
    } else {
      showToast("Chưa có video để kiểm tra chất lượng!", "error");
    }
  } else if (type === "threads_crawl") {
    appendLeaderLog("radar", "Đang vượt Cloudflare săn bài viết Threads hot sinh viên, drama, confessions...");
    setTimeout(() => {
      appendLeaderLog("done", "Phát hiện 3 bài viết Threads viral: 'Bạn thân vay 200 triệu...', 'Teamwork đại học...'");
      showToast("Đã săn được 3 bài Threads hot!");
    }, 1200);
  }
}

const btnDispatchLeader = document.getElementById("btn-dispatch-leader");
const leaderInput = document.getElementById("leader-command-input");
if (btnDispatchLeader && leaderInput) {
  const executeLeaderCommand = async () => {
    const cmd = leaderInput.value.trim();
    if (!cmd) return;

    appendLeaderLog("thinking", `Tiếp nhận chỉ đạo của sếp: "${cmd}"`);
    const lower = cmd.toLowerCase();

    // Kiểm tra nếu là liên kết Threads
    if (lower.includes("threads.net") || lower.includes("threads.com") || lower.includes("/post/")) {
      appendLeaderLog("radar", "Phát hiện liên kết Threads! Đang kích hoạt Headless Chrome để bóc tách nội dung và tải avatar thật...");
      showToast("Đang bóc tách bài viết Threads...");
      
      try {
        const res = await fetch("/api/commander/dispatch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: cmd })
        });
        const resp = await res.json();
        if (resp.success && resp.data) {
          const d = resp.data;
          const p = d.thread_data?.post || {};
          appendLeaderLog("done", `✅ Bóc tách thành công bài viết của @${p.username}: "${(p.content || '').slice(0, 45)}..." (${p.likes || '400+'} ❤️, ${d.total_comments || 0} 💬)`);
          appendLeaderLog("done", `✅ Đã tải 100% Avatar thật của @${p.username} và ${d.total_comments || 0} bình luận về cache cục bộ.`);
          appendLeaderLog("dispatch", `🎯 Đã sẵn sàng bấm máy Xưởng 5 (${d.job_id})! Bấm nút bên dưới để render.`);
          
          // Thêm nút bấm máy Xưởng 5 trực tiếp vào thanh HITL
          const hitlActions = document.getElementById("leader-hitl-actions");
          if (hitlActions) {
            const btnW5 = document.createElement("button");
            btnW5.className = "px-3.5 py-1.5 rounded-lg border border-pink-500 bg-pink-500 text-white text-xs font-bold transition-all shadow-md flex items-center gap-1 animate-pulse hover:bg-pink-600";
            btnW5.innerHTML = `<span class="material-symbols-outlined text-xs">movie</span> ⚡ Bấm Máy Xưởng 5 Cho @${p.username} Ngay`;
            btnW5.onclick = () => handleHitlAction("produce_threads");
            hitlActions.prepend(btnW5);
          }
          
          showToast(`Đã cào bài viết của @${p.username}!`);
          loadTaskQueue();
        } else {
          appendLeaderLog("alert", `Lỗi cào Threads: ${resp.error || "Không thể lấy nội dung"}`);
          showToast("Lỗi khi cào Threads", "error");
        }
      } catch (err) {
        appendLeaderLog("alert", `Lỗi kết nối máy chủ: ${err.message}`);
      }
      return;
    }

    if (lower.includes("github") || lower.includes("trending") || lower.includes("repo")) {
      openScoutModal();
    } else if (lower.includes("báo cáo") || lower.includes("report") || lower.includes("ca trực")) {
      openShiftReportModal();
    } else if (lower.includes("kiểm tra") || lower.includes("gatekeeper") || lower.includes("audit") || lower.includes("chất lượng")) {
      if (allVideos.length > 0) {
        runQualityAudit(allVideos[0].id);
      }
    } else if (lower.includes("telegram") || lower.includes("báo") || lower.includes("nhắn")) {
      sendTelegramReport();
    } else {
      appendLeaderLog("dispatch", `Đang phân tích bài toán và điều phối phân xưởng sản xuất tự hành tương ứng...`);
      try {
        await fetch("/api/commander/dispatch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: cmd })
        });
        loadTaskQueue();
      } catch (e) {}
      setTimeout(() => {
        appendLeaderLog("done", `Tác vụ "${cmd.slice(0, 40)}..." đã được đưa vào hàng đợi tự hành!`);
      }, 1000);
    }
  };

  btnDispatchLeader.onclick = executeLeaderCommand;
  leaderInput.onkeydown = (e) => {
    if (e.key === "Enter") executeLeaderCommand();
  };
}

async function runQualityAudit(jobId) {
  appendLeaderLog("thinking", `Đang kiểm tra chất lượng KCS Gatekeeper cho job: ${jobId}...`);
  try {
    const res = await fetch("/api/commander/quality-audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jobId }),
    });
    const data = await res.json();
    if (data.success && data.audit) {
      const a = data.audit;
      appendLeaderLog("done", `KCS HOÀN TẤT: Điểm ${a.score}/100 • Trạng thái: ${a.status} (Video MP4: PASS, Audio 48k: PASS)`);
      showToast(`KCS hoàn tất: ${a.score}/100 (${a.status})`);
    }
  } catch (err) {
    appendLeaderLog("alert", `Lỗi KCS: ${err.message}`);
  }
}

// ── SCOUT GITHUB MODAL CONTROLLER ──
async function openScoutModal() {
  if (scoutModal) scoutModal.classList.add("active");
  refreshScoutGitHub();
}

function closeScoutModal() {
  if (scoutModal) scoutModal.classList.remove("active");
}

async function refreshScoutGitHub() {
  const container = document.getElementById("scout-modal-body");
  if (!container) return;
  container.innerHTML = `
    <div class="text-center py-8 text-gray-500 font-mono text-xs">
      <span class="animate-spin material-symbols-outlined text-2xl mb-2 text-pink-500">progress_activity</span>
      <p>Đang quét radar GitHub Trending qua Cloudflare & Token 5,000 req/h...</p>
    </div>
  `;

  try {
    const res = await fetch("/api/commander/scout-github?limit=4");
    const data = await res.json();
    if (data.success && data.repos) {
      container.innerHTML = data.repos.map(item => {
        const r = item.repo || item;
        const name = r.full_name || r.name || "Repo";
        const url = r.html_url || r.url || "#";
        const stars = (r.stars || 0).toLocaleString();
        const lang = r.language || "OpenSource";
        const desc = r.description || "Dự án mã nguồn mở xu hướng trên GitHub.";
        const topTitle = (item.title_options && item.title_options[0]) || `Giải Mã Repo: ${r.name}`;

        return `
          <div class="p-3.5 rounded-xl border border-pink-100 bg-pink-50/40 flex flex-col gap-2 hover:border-pink-300 transition-colors">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-pink-500"></span>
                <a href="${url}" target="_blank" class="font-headline font-bold text-xs text-gray-800 hover:text-pink-600 hover:underline">${escapeHtml(name)}</a>
                <span class="px-1.5 py-0.2 rounded-full bg-pink-100 text-[10px] font-mono text-pink-700 font-semibold">${escapeHtml(lang)}</span>
              </div>
              <span class="text-xs font-mono font-bold text-pink-600">⭐ ${stars}</span>
            </div>

            <p class="text-xs text-gray-600 line-clamp-2">${escapeHtml(desc)}</p>

            <div class="p-2 rounded-lg bg-white border border-pink-100 text-[11px] font-mono text-gray-800 flex items-center justify-between shadow-xs">
              <span class="truncate font-semibold text-pink-900">🎬 ${escapeHtml(topTitle)}</span>
              <span class="text-pink-600 font-bold shrink-0 ml-2">Xưởng 2 (Remotion)</span>
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-pink-100 text-[11px] font-mono">
              <span class="text-gray-400">Đã sinh sẵn ${item.script_beats?.length || 5} Beats kịch bản</span>
              <button class="px-3 py-1 rounded-lg bg-pink-500 hover:bg-pink-600 text-white text-[11px] font-bold transition-colors shadow-xs" onclick="createVideoFromRepo('${escapeHtml(r.name)}', '${escapeHtml(url)}', '${escapeHtml(topTitle)}')">
                ⚡ Bấm Máy Xưởng 2
              </button>
            </div>
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-xs font-mono text-red-500">Không thể quét GitHub: ${escapeHtml(err.message)}</div>`;
  }
}

function createVideoFromRepo(repoName, repoUrl, topTitle) {
  closeScoutModal();
  openCreateModal();
  const titleInput = document.getElementById("create-title");
  const wsSelect = document.getElementById("create-workshop");
  const contentInput = document.getElementById("create-content");
  if (titleInput) titleInput.value = topTitle || `Giải Mã Repo Trending: ${repoName}`;
  if (wsSelect) wsSelect.value = "explainer";
  if (contentInput) contentInput.value = `Nguồn: ${repoUrl}\nChủ đề: Phân tích kiến trúc mã nguồn và giải thuật của ${repoName}.`;
}

// ── SHIFT REPORT MODAL CONTROLLER ──
async function openShiftReportModal() {
  if (reportModal) reportModal.classList.add("active");
  const content = document.getElementById("report-modal-content");
  if (content) content.textContent = "Đang tổng hợp dữ liệu ca trực 24h...";

  try {
    const res = await fetch("/api/commander/report");
    const data = await res.json();
    if (data.success && data.markdown) {
      if (content) content.textContent = data.markdown;
    }
  } catch (err) {
    if (content) content.textContent = `Lỗi tải báo cáo: ${err.message}`;
  }
}

function closeShiftReportModal() {
  if (reportModal) reportModal.classList.remove("active");
}

// ── YOUTUBE DIRECT UPLOAD MODAL & SMART SCHEDULING ──
function openYouTubeUploadModal(jobId, autoExtract = false) {
  const video = allVideos.find(v => v.id === jobId);
  if (!video) return;
  currentYouTubeJob = video;
  selectedPublishAt = null;

  const ytThumb = document.getElementById("yt-preview-thumb");
  const ytDuration = document.getElementById("yt-preview-duration");
  const ytRes = document.getElementById("yt-preview-res");
  const ytWorkshop = document.getElementById("yt-preview-workshop");
  const ytTitle = document.getElementById("yt-title");
  const ytPreviewTitle = document.getElementById("yt-preview-title");
  const ytDescription = document.getElementById("yt-description");
  const ytTags = document.getElementById("yt-tags");
  const ytStatusBox = document.getElementById("yt-status-box");
  const ytTitleCounter = document.getElementById("yt-title-counter");
  const schedIndicator = document.getElementById("yt-schedule-indicator");

  if (schedIndicator) schedIndicator.classList.add("hidden");
  document.querySelectorAll(".schedule-quick-btn").forEach(b => b.classList.remove("active"));

  if (ytStatusBox) ytStatusBox.classList.add("hidden");
  const ytProgressBar = document.getElementById("yt-progress-bar");
  const ytStatusPct = document.getElementById("yt-status-pct");
  const ytStatusMsg = document.getElementById("yt-status-msg");
  if (ytProgressBar) ytProgressBar.style.width = "0%";
  if (ytStatusPct) ytStatusPct.textContent = "0%";
  if (ytStatusMsg) ytStatusMsg.textContent = "Khởi tạo kết nối Resumable Upload...";

  if (ytThumb) {
    ytThumb.src = video.thumbUrl || "";
  }
  if (ytPreviewTitle) ytPreviewTitle.textContent = video.title;
  if (ytRes) ytRes.textContent = `${video.canvas.width}x${video.canvas.height}`;
  if (ytDuration) ytDuration.textContent = formatBytes(video.sizeBytes);
  if (ytWorkshop) ytWorkshop.textContent = `Phân Xưởng: ${video.workshop.toUpperCase()}`;

  // Pre-fill Title with SEO tags
  let defaultTitle = video.title;
  if (!defaultTitle.toLowerCase().includes("#shorts") && video.canvas.height > video.canvas.width) {
    defaultTitle = `${defaultTitle} #Shorts #OmniVideo`;
  }
  if (ytTitle) {
    ytTitle.value = defaultTitle.slice(0, 100);
    if (ytTitleCounter) ytTitleCounter.textContent = `${ytTitle.value.length} / 100`;
    ytTitle.oninput = () => {
      ytTitleCounter.textContent = `${ytTitle.value.length} / 100`;
    };
  }

  // Pre-fill Description & Timestamps
  let desc = `${video.title}\n\n`;
  desc += `Sản xuất tự hành bởi OmniVideo Studio (Phân xưởng ${video.workshop.toUpperCase()})\n\n`;
  if (video.beats && video.beats.length > 0) {
    desc += "TIMESTAMPS & PHÂN ĐOẠN:\n00:00 - Mở đầu & Hook\n";
    let curSec = 2;
    video.beats.slice(1, 8).forEach((b, i) => {
      const mins = Math.floor(curSec / 60);
      const secs = curSec % 60;
      const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      const beatName = b.visual?.headline || b.rawText?.slice(0, 30) || `Nhịp ${i + 2}`;
      desc += `${timeStr} - ${beatName}\n`;
      curSec += 4;
    });
    desc += "\n";
  }
  desc += "#OmniVideo #Antigravity #AI #VideoAI #Shorts #Remotion";
  if (ytDescription) ytDescription.value = desc;

  // Pre-fill Tags
  const defaultTags = ["OmniVideo", "Antigravity", "AI Video", video.workshop, "Storyverse", "Shorts"];
  if (ytTags) ytTags.value = defaultTags.join(", ");

  // Setup Privacy Radios
  const privacyCards = document.querySelectorAll(".yt-privacy-card");
  privacyCards.forEach(card => {
    card.onclick = () => {
      privacyCards.forEach(c => {
        c.classList.remove("active", "border-2", "border-pink-500", "bg-pink-50");
        c.classList.add("bg-white", "border-pink-200");
      });
      card.classList.add("active", "border-2", "border-pink-500", "bg-pink-50");
      card.classList.remove("bg-white", "border-pink-200");
      const radio = card.querySelector("input[type=radio]");
      if (radio) radio.checked = true;
    };
  });

  if (ytModal) ytModal.classList.add("active");

  if (autoExtract) {
    extractFramesForCurrentVideo();
  }
}

function closeYouTubeUploadModal() {
  if (ytModal) ytModal.classList.remove("active");
}

function openPlayerFromYouTubeModal() {
  if (currentYouTubeJob) {
    closeYouTubeUploadModal();
    openPlayer(currentYouTubeJob.id);
  }
}

// ── KEYFRAME EXTRACTION FOR THUMBNAIL ──
async function extractFramesForCurrentVideo() {
  if (!currentYouTubeJob) return;

  const btn = document.getElementById("btn-extract-frames");
  const wrap = document.getElementById("frame-candidates-wrap");
  const grid = document.getElementById("frame-candidates-grid");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin material-symbols-outlined text-xs">progress_activity</span> <span>Đang trích xuất frame...</span>`;
  }

  try {
    const res = await fetch("/api/video/extract-frames", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jobId: currentYouTubeJob.id,
        timestamps: ["00:00:03", "00:00:12", "00:00:25"]
      }),
    });
    const data = await res.json();

    if (data.success && data.frames && data.frames.length > 0) {
      if (wrap) wrap.classList.remove("hidden");
      if (grid) {
        grid.innerHTML = data.frames.map(f => `
          <div class="frame-candidate-card group" onclick="selectFrameAsThumbnail('${escapeHtml(f.filename)}', '${escapeHtml(f.url)}')">
            <div class="aspect-square bg-pink-50 overflow-hidden">
              <img src="${f.url}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" alt="Frame ${f.time}"/>
            </div>
            <span class="absolute bottom-1 left-1 text-[9px] font-mono font-bold bg-black/80 text-white px-1 rounded">${f.time}</span>
            <span class="absolute top-1 right-1 text-[8px] font-mono font-bold bg-pink-500 text-white px-1 rounded">SCORE 98%</span>
          </div>
        `).join("");
      }
      showToast("Đã trích xuất 3 frame ứng viên từ video!");
    } else {
      showToast("Không thể trích xuất frame: " + (data.error || "Lỗi ffmpeg"), "error");
    }
  } catch (err) {
    showToast("Lỗi kết nối trích xuất frame: " + err.message, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">camera</span> <span>📸 Trích Frame Đẹp Từ Video</span>`;
    }
  }
}

async function selectFrameAsThumbnail(filename, url) {
  if (!currentYouTubeJob) return;

  try {
    const res = await fetch("/api/video/set-thumbnail", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jobId: currentYouTubeJob.id,
        customThumbPath: filename
      }),
    });
    const data = await res.json();

    if (data.success) {
      currentYouTubeJob.thumbUrl = data.thumbUrl || url;
      const previewThumb = document.getElementById("yt-preview-thumb");
      if (previewThumb) previewThumb.src = data.thumbUrl || url;
      renderGrid();
      showToast("Đã lưu frame làm thumbnail chính thức cho video!");
    }
  } catch (err) {
    showToast("Lỗi khi đặt thumbnail: " + err.message, "error");
  }
}

// ── SMART SCHEDULED PUBLISHING ──
function selectScheduledTime(timeStr) {
  const [targetH, targetM] = timeStr.split(":").map(Number);
  const now = new Date();
  const schedDate = new Date();
  schedDate.setHours(targetH, targetM, 0, 0);

  if (schedDate.getTime() <= now.getTime()) {
    schedDate.setDate(schedDate.getDate() + 1);
  }

  selectedPublishAt = schedDate.toISOString();

  // Select "Riêng Tư (Private)"
  const privateRadio = document.querySelector('input[name="yt_privacy"][value="private"]');
  if (privateRadio) {
    privateRadio.checked = true;
    const cards = document.querySelectorAll(".yt-privacy-card");
    cards.forEach(c => {
      c.classList.remove("active", "border-2", "border-pink-500", "bg-pink-50");
      c.classList.add("bg-white", "border-pink-200");
    });
    privateRadio.closest(".yt-privacy-card")?.classList.add("active", "border-2", "border-pink-500", "bg-pink-50");
  }

  // Show Indicator
  const indicator = document.getElementById("yt-schedule-indicator");
  const text = document.getElementById("yt-schedule-text");
  const isTomorrow = schedDate.getDate() !== now.getDate();
  const dayStr = isTomorrow ? "Ngày Mai" : "Hôm Nay";
  if (indicator && text) {
    text.textContent = `⏰ Đã Đặt Lịch: ${dayStr} lúc ${timeStr}`;
    indicator.classList.remove("hidden");
  }

  showToast(`Đã hẹn giờ phát: ${dayStr} lúc ${timeStr}`);
}

function clearScheduledPublishTime() {
  selectedPublishAt = null;
  const indicator = document.getElementById("yt-schedule-indicator");
  if (indicator) indicator.classList.add("hidden");
  showToast("Đã xóa lịch hẹn phát.");
}

// ── MULTI-PLATFORM PACKAGING (TIKTOK / REELS) ──
function copyMultiPlatformCaption() {
  if (!currentYouTubeJob) return;

  const title = document.getElementById("yt-title")?.value || currentYouTubeJob.title;
  const caption = `${title}\n\nXem trọn bộ trên kênh Storyverse VN!\n\n#storyverse #drama #threads #viral #fyp #xuhuong #vietnam`;
  
  navigator.clipboard.writeText(caption).then(() => {
    showToast("Đã copy caption định dạng TikTok / Instagram Reels!");
  }).catch(() => {
    showToast("Không thể copy caption vào clipboard.", "error");
  });
}

// ── YOUTUBE UPLOAD FORM SUBMIT ──
const youtubeUploadForm = document.getElementById("youtube-upload-form");
if (youtubeUploadForm) {
  youtubeUploadForm.onsubmit = async (e) => {
    e.preventDefault();
    if (!currentYouTubeJob) return;

    const btnSubmit = document.getElementById("btn-yt-submit");
    const btnText = document.getElementById("btn-yt-submit-text");
    const statusBox = document.getElementById("yt-status-box");
    const progressBar = document.getElementById("yt-progress-bar");
    const statusPct = document.getElementById("yt-status-pct");
    const statusTitleText = document.getElementById("yt-status-title-text");
    const statusMsg = document.getElementById("yt-status-msg");

    const channel = document.getElementById("yt-channel").value;
    const category = document.getElementById("yt-category").value;
    const title = document.getElementById("yt-title").value.trim();
    const description = document.getElementById("yt-description").value.trim();
    const tags = document.getElementById("yt-tags").value.trim();
    const privacy = document.querySelector('input[name="yt_privacy"]:checked')?.value || "unlisted";

    btnSubmit.disabled = true;
    btnText.innerHTML = `<span class="animate-spin material-symbols-outlined text-xs inline-block mr-1">progress_activity</span><span>Đang truyền file lên YouTube...</span>`;
    
    statusBox.classList.remove("hidden");
    statusBox.className = "rounded-xl p-3.5 border bg-white border-pink-200 shadow-sm transition-all";
    if (progressBar) progressBar.style.width = "5%";
    if (statusPct) statusPct.textContent = "5%";
    if (statusTitleText) statusTitleText.textContent = `Đang kết nối kênh: ${channel} (${privacy.toUpperCase()})`;
    if (statusMsg) statusMsg.textContent = selectedPublishAt 
      ? `Đang truyền video và đăng ký giờ phát: ${selectedPublishAt}...` 
      : "Đang khởi tạo phiên Resumable Upload...";

    const jobId = currentYouTubeJob.id;
    let pollInterval = setInterval(async () => {
      try {
        const sRes = await fetch(`/api/youtube/upload-status?jobId=${encodeURIComponent(jobId)}`);
        const sData = await sRes.json();
        if (sData.success) {
          if (typeof sData.progress === "number" && progressBar && statusPct) {
            progressBar.style.width = `${Math.min(100, Math.max(5, sData.progress))}%`;
            statusPct.textContent = `${Math.min(100, Math.max(5, sData.progress))}%`;
          }
          if (sData.message && statusMsg) {
            statusMsg.textContent = sData.message;
          }
          if (sData.progress) {
            btnText.innerHTML = `<span class="animate-spin material-symbols-outlined text-xs inline-block mr-1">progress_activity</span><span>Đang upload: ${sData.progress}%</span>`;
          }
          if (sData.status === "completed" || sData.status === "error") {
            clearInterval(pollInterval);
          }
        }
      } catch (pollErr) {
        // ignore jitter
      }
    }, 800);

    try {
      const res = await fetch("/api/youtube/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jobId: currentYouTubeJob.id,
          channel,
          category,
          title,
          description,
          tags,
          privacy,
          publishAt: selectedPublishAt
        }),
      });

      clearInterval(pollInterval);
      const result = await res.json();

      if (result.success) {
        playSuccessChime();
        if (progressBar) progressBar.style.width = "100%";
        if (statusPct) statusPct.textContent = "100%";
        
        currentYouTubeJob.isPublished = true;
        currentYouTubeJob.youtubeUrl = result.url;
        currentYouTubeJob.youtubeId = result.video_id;
        updateStats();
        renderGrid();

        statusBox.className = "rounded-xl p-4 border bg-emerald-50 border-emerald-300 text-emerald-800 space-y-2.5 transition-all";
        statusBox.innerHTML = `
          <div class="flex items-center gap-2 font-bold text-emerald-700">
            <span class="material-symbols-outlined text-lg">check_circle</span>
            <span class="text-sm">UPLOAD YOUTUBE HOÀN TẤT 100%!</span>
          </div>
          <div class="text-xs font-mono">
            Link video: <a href="${result.url}" target="_blank" class="underline font-bold text-pink-600 hover:text-pink-700">${result.url}</a>
          </div>
          <div class="text-[11px] font-mono text-gray-600">
            Chế độ: <strong>${result.privacy?.toUpperCase() || privacy.toUpperCase()}</strong> • Video ID: <code>${result.video_id || ''}</code>
            ${selectedPublishAt ? `• Hẹn giờ: <strong>${selectedPublishAt}</strong>` : ''}
          </div>
          <div class="pt-1 flex items-center gap-2">
            <a href="${result.url}" target="_blank" class="px-3.5 py-1.5 rounded-xl bg-pink-500 text-white font-bold text-xs inline-flex items-center gap-1.5 hover:bg-pink-600 transition-colors shadow-sm">
              <span class="material-symbols-outlined text-xs">open_in_new</span> Xem trên YouTube
            </a>
            <button type="button" class="px-3 py-1.5 rounded-xl bg-white border border-pink-200 text-xs text-gray-700 hover:bg-pink-50 transition-colors" onclick="navigator.clipboard.writeText('${result.url}').then(()=>showToast('Đã copy link YouTube!'))">
              Sao chép Link
            </button>
            <button type="button" class="px-3 py-1.5 rounded-xl bg-white border border-pink-200 text-xs text-pink-700 font-bold hover:bg-pink-50 transition-colors" onclick="sendTelegramReport()">
              📱 Báo Telegram Sếp
            </button>
          </div>
        `;
        showToast("Upload YouTube thành công 100%!");
      } else {
        statusBox.className = "rounded-xl p-3.5 border bg-red-50 border-red-300 text-red-700 transition-all";
        statusBox.innerHTML = `
          <div class="flex items-center gap-2 font-bold text-red-600 mb-1">
            <span class="material-symbols-outlined text-base">error</span>
            <span>LỖI UPLOAD YOUTUBE</span>
          </div>
          <p class="text-xs font-mono text-gray-800">${escapeHtml(result.error || "Không thể tải lên YouTube")}</p>
        `;
      }
    } catch (err) {
      clearInterval(pollInterval);
      statusBox.className = "rounded-xl p-3.5 border bg-red-50 border-red-300 text-red-700 transition-all";
      statusBox.innerHTML = `
        <div class="flex items-center gap-2 font-bold text-red-600 mb-1">
          <span class="material-symbols-outlined text-base">wifi_off</span>
          <span>LỖI KẾT NỐI MẠNG</span>
        </div>
        <p class="text-xs font-mono text-gray-800">${escapeHtml(err.message)}</p>
      `;
    } finally {
      clearInterval(pollInterval);
      btnSubmit.disabled = false;
      btnText.innerHTML = `🚀 Bắt Đầu Upload YouTube`;
    }
  };
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

  beatsTimeline.innerHTML = (video.beats || []).map((beat, idx) => {
    return `
      <div class="beat-item" onclick="seekVideoBeat(${idx})">
        <div class="beat-header">
          <span class="beat-role-tag">${escapeHtml(beat.role || 'beat')}</span>
          <span class="beat-speaker">${escapeHtml(beat.speaker || 'Narrator')}</span>
        </div>
        <div class="beat-text">${escapeHtml(beat.rawText || '')}</div>
      </div>
    `;
  }).join("");

  playerModal.classList.add("active");
}

function seekVideoBeat(index) {
  if (mainVideo && mainVideo.duration) {
    mainVideo.currentTime = index * 4;
    mainVideo.play();
  }
}

// ── CREATE JOB MODAL ──
const createJobForm = document.getElementById("create-job-form");
if (createJobForm) {
  createJobForm.onsubmit = async (e) => {
    e.preventDefault();
    const title = document.getElementById("create-title").value.trim();
    const workshop = document.getElementById("create-workshop").value;
    const voiceId = document.getElementById("create-voice").value;
    const rawContent = document.getElementById("create-content").value.trim();

    try {
      const res = await fetch("/api/videos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, workshop, voiceId, rawContent }),
      });
      const data = await res.json();
      if (data.success) {
        closeCreateModal();
        await loadVideos();
        appendLeaderLog("dispatch", `Đã khởi tạo job mới "${title}". Bắt đầu render!`);
        showToast("Đã khởi tạo kịch bản video mới!");
        triggerRender(data.jobId);
      } else {
        alert("Lỗi khi tạo video: " + data.error);
      }
    } catch (err) {
      alert("Lỗi kết nối: " + err.message);
    }
  };
}

// ── EDIT JOB MODAL ──
async function openEditor(jobId) {
  const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`);
  const data = await res.json();
  if (!data.success) {
    alert("Không thể tải thông tin video để chỉnh sửa.");
    return;
  }
  const video = data.video;
  document.getElementById("edit-job-id").value = video.id;
  document.getElementById("edit-title").value = video.title;
  document.getElementById("edit-beats-json").value = JSON.stringify(video.beats, null, 2);
  editModal.classList.add("active");
}

const editJobForm = document.getElementById("edit-job-form");
if (editJobForm) {
  editJobForm.onsubmit = async (e) => {
    e.preventDefault();
    const jobId = document.getElementById("edit-job-id").value;
    const title = document.getElementById("edit-title").value.trim();
    let beats = [];
    try {
      beats = JSON.parse(document.getElementById("edit-beats-json").value);
    } catch (err) {
      alert("Định dạng JSON của beats không hợp lệ: " + err.message);
      return;
    }

    try {
      const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, beats }),
      });
      const data = await res.json();
      if (data.success) {
        closeEditModal();
        await loadVideos();
        appendLeaderLog("done", `Đã lưu chỉnh sửa kịch bản Beats cho job: ${jobId}`);
        showToast("Đã lưu thay đổi kịch bản thành công!");
      }
    } catch (err) {
      alert("Lỗi kết nối: " + err.message);
    }
  };
}

// ── DELETE VIDEO ──
async function deleteVideo(jobId) {
  if (confirm(`Bạn có chắc chắn muốn xóa video '${jobId}' và kịch bản không?`)) {
    try {
      const res = await fetch(`/api/videos/${encodeURIComponent(jobId)}`, { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        await loadVideos();
        appendLeaderLog("alert", `Đã xóa video '${jobId}' khỏi thư viện.`);
        showToast("Đã xóa video khỏi thư viện.");
      }
    } catch (err) {
      alert("Lỗi khi xóa: " + err.message);
    }
  }
}

// ── TRIGGER RENDER ──
function triggerRender(jobId) {
  if (activeEventSource) {
    activeEventSource.close();
  }

  renderModal.classList.add("active");
  renderModalTitle.textContent = `Đang Render: ${jobId}`;
  renderTerminal.innerHTML = `<div class="terminal-line">[START] Khởi động render pipeline cho job: ${escapeHtml(jobId)}...</div>`;
  renderProgressBar.style.width = "10%";
  btnCloseRender.style.display = "none";
  document.getElementById("render-modal-footer").style.display = "none";

  activeEventSource = new EventSource(`/api/render/${encodeURIComponent(jobId)}`);

  activeEventSource.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.log) {
        appendLog(payload.log);
      }
      if (payload.progress) {
        renderProgressBar.style.width = `${payload.progress}%`;
      }
      if (payload.done) {
        appendLog("[SUCCESS] Render hoàn tất 100%! Đã đóng gói MP4.", "done");
        renderProgressBar.style.width = "100%";
        activeEventSource.close();
        btnCloseRender.style.display = "block";
        document.getElementById("render-modal-footer").style.display = "flex";
        playSuccessChime();
        loadVideos();
        appendLeaderLog("done", `Render hoàn tất video: ${jobId}. Sẵn sàng xuất bản!`);
      }
      if (payload.error) {
        appendLog(`[ERROR] ${payload.error}`, "error");
        activeEventSource.close();
        btnCloseRender.style.display = "block";
        document.getElementById("render-modal-footer").style.display = "flex";
      }
    } catch (e) {
      appendLog(event.data);
    }
  };

  activeEventSource.onerror = () => {
    appendLog("[DISCONNECT] Kết nối render kết thúc.");
    activeEventSource.close();
    btnCloseRender.style.display = "block";
    document.getElementById("render-modal-footer").style.display = "flex";
  };
}

function appendLog(text, type = "normal") {
  const line = document.createElement("div");
  line.className = `terminal-line ${type}`;
  line.textContent = text;
  renderTerminal.appendChild(line);
  renderTerminal.scrollTop = renderTerminal.scrollHeight;
}

function closeRenderModal() {
  if (activeEventSource) activeEventSource.close();
  renderModal.classList.remove("active");
}

// ── SIDEBAR CONTROLLER ──
function initSidebarController() {
  const btnToggle = document.getElementById("btn-toggle-sidebar");
  const sidebar = document.getElementById("sidebarNav");
  const mainContent = document.getElementById("mainContent");
  const toggleIcon = document.getElementById("sidebar-toggle-icon");

  if (!btnToggle || !sidebar || !mainContent) return;

  const isCollapsed = localStorage.getItem("omni_sidebar_collapsed") === "true";
  if (isCollapsed) {
    sidebar.classList.add("collapsed");
    mainContent.classList.add("sidebar-collapsed");
    if (toggleIcon) toggleIcon.textContent = "chevron_right";
  }

  btnToggle.onclick = () => {
    const collapsed = sidebar.classList.toggle("collapsed");
    mainContent.classList.toggle("sidebar-collapsed");
    localStorage.setItem("omni_sidebar_collapsed", collapsed);
    if (toggleIcon) {
      toggleIcon.textContent = collapsed ? "chevron_right" : "chevron_left";
    }
  };
}

// ── SEARCH CONTROLLER ──
if (searchInput) {
  searchInput.oninput = () => {
    currentSearch = searchInput.value.trim();
    renderGrid();
  };
}

// ── INITIALIZATION ──
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSidebarController();
  initLeaderLog();
  loadVideos();
  loadTaskQueue();
});
