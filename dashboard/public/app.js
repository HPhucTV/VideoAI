
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

// ── WORKSHOP CATEGORY FILTER CONTROLLER (STITCH MCP SEGMENTED PILL) ──
function setActiveWorkshopFilter(workshop, btnElement) {
  currentFilter = workshop;
  document.querySelectorAll(".workshop-filter-btn").forEach(btn => {
    btn.classList.remove("active");
  });
  if (btnElement) {
    btnElement.classList.add("active");
  } else {
    const match = document.querySelector(`.workshop-filter-btn[data-filter="${workshop}"]`);
    if (match) match.classList.add("active");
  }
  renderGrid();
}

function filterByWorkshop(workshop) {
  const btn = document.querySelector(`.workshop-filter-btn[data-filter="${workshop}"]`);
  setActiveWorkshopFilter(workshop, btn);
}

function updateCategoryBadges() {
  if (!allVideos) return;
  const counts = {
    all: allVideos.length,
    threads: allVideos.filter(v => v.workshop === "threads").length,
    cinematic: allVideos.filter(v => v.workshop === "cinematic").length,
    explainer: allVideos.filter(v => v.workshop === "explainer").length,
    whiteboard: allVideos.filter(v => v.workshop === "whiteboard").length,
    news: allVideos.filter(v => v.workshop === "news").length,
  };
  for (const [k, v] of Object.entries(counts)) {
    const el = document.getElementById(`badge-count-${k}`);
    if (el) el.textContent = v;
  }
}

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
// ================= ANTIGRAVITY 2.0 LIVE BRIDGE & 7-GATE PRODUCTION STEPPER =================
let antigravityEventSource = null;
let currentHighestGate = 1;
let lastAnnouncedGate = 0;
let currentTerminalFilter = "all";
const liveAntigravityEvents = [];

function appendLeaderLog(tag, message) {
  if (!leaderLogStream) return;
  const time = new Date().toLocaleTimeString("vi-VN");
  const line = document.createElement("div");
  line.className = "terminal-line animate-in fade-in duration-150";

  let cat = "all";
  let tagClass = "term-system";
  const tLower = (tag || "").toLowerCase();
  if (tLower.includes("think")) { cat = "thought"; tagClass = "term-thought"; }
  else if (tLower.includes("tool") || tLower.includes("radar") || tLower.includes("done")) { cat = "tool"; tagClass = "term-tool"; }
  else if (tLower.includes("gate") || tLower.includes("dispatch")) { cat = "gate"; tagClass = "term-gate"; }
  else if (tLower.includes("user")) { cat = "gate"; tagClass = "term-user"; }

  line.dataset.category = cat;
  if (currentTerminalFilter !== "all" && currentTerminalFilter !== cat) {
    line.style.display = "none";
  }

  line.innerHTML = `
    <span class="term-time">[${time}]</span>
    <span class="term-tag ${tagClass}">[${tag.toUpperCase()}]</span>
    <span class="flex-1 text-gray-800 break-words">${escapeHtml(message)}</span>
  `;

  leaderLogStream.appendChild(line);
  leaderLogStream.scrollTop = leaderLogStream.scrollHeight;
}

function appendLiveStreamLine(time, tag, tagClass, text, category = "all") {
  const leaderLogStream = document.getElementById("leader-log-stream");
  if (!leaderLogStream) return;

  const line = document.createElement("div");
  line.className = "terminal-line";
  line.dataset.category = category;

  if (currentTerminalFilter !== "all" && currentTerminalFilter !== category) {
    line.style.display = "none";
  }

  line.innerHTML = `
    <span class="term-time">[${time}]</span>
    <span class="term-tag ${tagClass}">[${tag}]</span>
    <span class="flex-1 text-gray-800 break-words">${escapeHtml(text)}</span>
  `;

  leaderLogStream.appendChild(line);
  leaderLogStream.scrollTop = leaderLogStream.scrollHeight;
}

function initAntigravityBridge() {
  if (antigravityEventSource) {
    antigravityEventSource.close();
  }

  const missionStatusText = document.getElementById("mission-status-text");
  const missionStatusDot = document.getElementById("mission-status-dot");
  const missionConvoId = document.getElementById("mission-convo-id");
  const antigravityGateBadge = document.getElementById("antigravity-gate-badge");
  const gateOverallProgress = document.getElementById("gate-overall-progress");
  const terminalStepIndicator = document.getElementById("terminal-step-indicator");
  const leaderLogStream = document.getElementById("leader-log-stream");
  const btnDispatchAntigravity = document.getElementById("btn-dispatch-antigravity");
  const dispatchFeedback = document.getElementById("dispatch-feedback");

  try {
    antigravityEventSource = new EventSource("/api/antigravity/stream");

    antigravityEventSource.onopen = () => {
      if (missionStatusText) missionStatusText.textContent = "ĐỒNG BỘ HAI CHIỀU ANTIGRAVITY 2.0";
      if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
    };

    antigravityEventSource.addEventListener("init", (e) => {
      try {
        const data = JSON.parse(e.data);
        const session = data.session || data.activeSession;
        const cId = session?.conversationId || (typeof session === "string" ? session : null);
        if (cId) {
          if (missionConvoId) missionConvoId.textContent = cId.slice(0, 10) + "...";
          if (missionStatusText) missionStatusText.textContent = "ĐỒNG BỘ HAI CHIỀU ANTIGRAVITY 2.0";
          if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
        }
        if (data.studioState) {
          const s = data.studioState;
          currentHighestGate = s.currentGate || 1;
          updateGateStepper(s.currentGate, s.gateName, s.progressPercent, s.isCompleted, s.completedGates);
        }
      } catch (err) {
        console.warn("Lỗi xử lý init SSE:", err);
      }
    });

    antigravityEventSource.addEventListener("gate_state", (e) => {
      try {
        const state = JSON.parse(e.data);
        if (state && state.currentGate) {
          currentHighestGate = Math.max(currentHighestGate, state.currentGate);
          updateGateStepper(
            state.currentGate,
            state.gateName,
            state.progressPercent,
            state.isCompleted,
            state.completedGates
          );
        }
      } catch (_) {}
    });

    antigravityEventSource.addEventListener("task_queue", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data && data.queue) {
          const badgeHeader = document.getElementById("queue-badge-count-header");
          const countFooter = document.getElementById("queue-footer-count");
          if (badgeHeader) badgeHeader.textContent = data.queue.length;
          if (countFooter) countFooter.textContent = data.queue.length;
          const modal = document.getElementById("task-queue-modal");
          if (modal && modal.classList.contains("active")) {
            loadTaskQueue();
          }
        }
      } catch (_) {}
    });

    antigravityEventSource.addEventListener("history", (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.events && Array.isArray(data.events)) {
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

    antigravityEventSource.onerror = () => {
      if (missionStatusText) missionStatusText.textContent = "MẤT KẾT NỐI ANTIGRAVITY 2.0";
      if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-rose-500";
    };
  } catch (err) {
    console.error("Lỗi khởi tạo Antigravity EventSource:", err);
  }

  // ── TERMINAL FILTERS ──
  document.querySelectorAll(".terminal-filter-btn").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".terminal-filter-btn").forEach(b => {
        b.classList.remove("active", "bg-pink-500", "text-white");
        b.classList.add("text-gray-600");
      });
      btn.classList.add("active", "bg-pink-500", "text-white");
      btn.classList.remove("text-gray-600");

      currentTerminalFilter = btn.dataset.filter || "all";
      const lines = leaderLogStream ? leaderLogStream.querySelectorAll(".terminal-line") : [];
      lines.forEach(line => {
        if (currentTerminalFilter === "all" || line.dataset.category === currentTerminalFilter) {
          line.style.display = "flex";
        } else {
          line.style.display = "none";
        }
      });
    };
  });

  // ── DIRECT DISPATCH TO ANTIGRAVITY IDE 2.0 (IPC) ──
  if (btnDispatchAntigravity) {
    btnDispatchAntigravity.onclick = async () => {
      const leaderInput = document.getElementById("leader-command-input");
      const cmd = leaderInput ? leaderInput.value.trim() : "";
      if (!cmd) {
        showToast("Vui lòng nhập link bài viết hoặc yêu cầu kịch bản!", "warning");
        return;
      }

      const workshop = document.getElementById("dispatch-workshop")?.value || "threads";
      const bg = document.getElementById("dispatch-bg")?.value || "minecraft_parkour.mp4";
      const speed = document.getElementById("dispatch-speed")?.value || "1.25";
      const autoPublish = document.getElementById("dispatch-publish")?.checked ?? true;

      btnDispatchAntigravity.disabled = true;
      btnDispatchAntigravity.innerHTML = `<span class="material-symbols-outlined text-[15px] animate-spin">sync</span> <span>Đang Bắn...</span>`;

      appendLeaderLog("thinking", `Bắn lệnh điều phối trực tiếp xuống Antigravity IDE 2.0: "${cmd.slice(0, 50)}..."`);

      try {
        const res = await fetch("/api/antigravity/dispatch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: cmd,
            workshop,
            background: bg,
            speed,
            autoPublish
          })
        });
        const data = await res.json();

        if (dispatchFeedback) {
          dispatchFeedback.classList.remove("hidden");
          if (data.success) {
            dispatchFeedback.className = "p-2.5 rounded-lg text-xs font-mono bg-emerald-50 border border-emerald-300 text-emerald-800";
            dispatchFeedback.innerHTML = `✅ <strong>Đã bắn lệnh thành công vào Antigravity IDE 2.0!</strong><br/>Agent đang tiếp nhận và bắt đầu quy trình 7 Cổng Sản Xuất.`;
            currentHighestGate = 1;
            lastAnnouncedGate = 1;
            updateGateStepper(1, "Ý Tưởng & Tiếp Nhận", 25, false, [1]);
            appendLeaderLog("dispatch", `Đã gửi thông điệp vào Antigravity session. IDE đang tự động thực thi...`);
            showToast("Đã bắn request vào Antigravity IDE 2.0!");
          } else {
            dispatchFeedback.className = "p-2.5 rounded-lg text-xs font-mono bg-rose-50 border border-rose-300 text-rose-800";
            dispatchFeedback.innerHTML = `❌ <strong>Lỗi:</strong> ${escapeHtml(data.error || "Không thể gửi lệnh")}`;
            showToast("Lỗi khi bắn lệnh vào IDE", "error");
          }
          setTimeout(() => {
            dispatchFeedback.classList.add("hidden");
          }, 6000);
        }
      } catch (err) {
        showToast("Lỗi kết nối IPC: " + err.message, "error");
      } finally {
        btnDispatchAntigravity.disabled = false;
        btnDispatchAntigravity.innerHTML = `<span class="material-symbols-outlined text-[15px]">send</span> <span>Bắn Vào IDE 2.0</span>`;
      }
    };
  }
}

// ── FAST HUMAN-IN-THE-LOOP (HITL) APPROVAL BUTTONS ──
window.quickApproveGate = async function(gate) {
  const missionStatusText = document.getElementById("mission-status-text");
  const missionStatusDot = document.getElementById("mission-status-dot");
  if (missionStatusText) missionStatusText.textContent = "ĐANG PHÊ DUYỆT CỔNG...";
  if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping";

  appendLeaderLog("dispatch", `Sếp phê duyệt nhanh HITL: "${gate}". Đang bắn thông điệp phê duyệt vào Antigravity IDE...`);
  showToast(`Đang phê duyệt: ${gate}...`);

  try {
    const res = await fetch("/api/antigravity/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gate })
    });
    const result = await res.json();

    if (result.success) {
      appendLeaderLog("done", `✅ Đã chuyển lệnh phê duyệt thành công vào Antigravity IDE! Agent đang tiếp tục tiến trình...`);
      showToast(`Đã duyệt thành công: ${gate}!`);
      if (currentHighestGate < 7) {
        updateGateStepper(currentHighestGate + 1, "Đang xử lý sau phê duyệt", 40);
      }
    } else {
      appendLeaderLog("alert", `❌ Không thể gửi phê duyệt: ${result.error || "Lỗi không xác định"}`);
      showToast("Lỗi gửi phê duyệt: " + (result.error || ""), "error");
    }
  } catch (err) {
    appendLeaderLog("alert", `❌ Lỗi kết nối IPC: ${err.message}`);
    showToast("Lỗi kết nối: " + err.message, "error");
  } finally {
    if (missionStatusText) missionStatusText.textContent = "ĐỒNG BỘ HAI CHIỀU ANTIGRAVITY 2.0";
    if (missionStatusDot) missionStatusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse";
  }
};

// ── UPDATE 7-GATE STEPPER (MONOTONIC & REAL-TIME) ──
function updateGateStepper(gateNumber, gateName, progressPercent = 75, isCompleted = false, completedGates = []) {
  const antigravityGateBadge = document.getElementById("antigravity-gate-badge");
  const gateOverallProgress = document.getElementById("gate-overall-progress");

  if (antigravityGateBadge) {
    if (isCompleted && gateNumber >= 6) {
      antigravityGateBadge.textContent = `Cổng ${gateNumber}: Hoàn Thành`;
    } else {
      antigravityGateBadge.textContent = `Cổng ${gateNumber}`;
    }
  }

  if (gateOverallProgress) {
    if (isCompleted && gateNumber >= 6) {
      gateOverallProgress.textContent = `Tiến độ: 100% (Cổng ${gateNumber}/7: ${gateName} 🎉)`;
    } else {
      const overall = Math.min(100, Math.round(((gateNumber - 1) * 100 + progressPercent) / 7));
      gateOverallProgress.textContent = `Tiến độ: ${overall}% (Cổng ${gateNumber}/7: ${gateName})`;
    }
  }

  const doneSet = new Set(Array.isArray(completedGates) ? completedGates : []);
  if (isCompleted) {
    for (let k = 1; k <= gateNumber; k++) doneSet.add(k);
  }

  for (let i = 1; i <= 7; i++) {
    const card = document.getElementById(`gate-card-${i}`);
    const icon = document.getElementById(`gate-icon-${i}`);
    const bar = document.getElementById(`gate-bar-${i}`);
    if (!card || !bar) continue;

    card.className = "gate-card p-3 rounded-xl border flex flex-col gap-1.5 transition-all shadow-xs ";

    if (doneSet.has(i) || i < gateNumber || (isCompleted && i <= gateNumber)) {
      // Completed gate
      card.className += "border-emerald-300 bg-emerald-50/60 gate-done";
      if (icon) {
        icon.className = "material-symbols-outlined text-[15px] text-emerald-600 font-bold";
        icon.textContent = "check_circle";
      }
      bar.className = "bg-emerald-500 h-full rounded-full w-full";
      bar.style.width = "100%";
    } else if (i === gateNumber && !isCompleted) {
      // Currently active gate
      card.className += "border-2 border-pink-500 bg-pink-50 gate-active ring-2 ring-pink-200/50 shadow-md";
      if (icon) {
        icon.className = "w-2.5 h-2.5 rounded-full bg-pink-500 animate-ping self-center";
        icon.textContent = "";
      }
      bar.className = "bg-pink-500 h-full rounded-full transition-all duration-300";
      bar.style.width = `${Math.max(15, progressPercent)}%`;
    } else {
      // Pending gate
      card.className += "border-pink-100 bg-white gate-pending opacity-70";
      if (icon) {
        icon.className = "material-symbols-outlined text-[15px] text-gray-300";
        icon.textContent = "radio_button_unchecked";
      }
      bar.className = "bg-pink-200 h-full rounded-full";
      bar.style.width = "0%";
    }
  }
}

// ── PROCESS INCOMING SSE EVENT ──
function processIncomingEvent(ev) {
  liveAntigravityEvents.push(ev);
  const now = ev.timestamp ? new Date(ev.timestamp) : new Date();
  const time = now.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const terminalStepIndicator = document.getElementById("terminal-step-indicator");
  if (terminalStepIndicator && ev.stepIndex) {
    terminalStepIndicator.textContent = `Bước #${ev.stepIndex}: ${ev.type || "Hoạt động"}`;
  }

  // Cập nhật Cổng quy trình nếu có
  const gateObj = ev.gate || ev.gateProgress;
  if (gateObj && gateObj.gateNumber) {
    const gNum = gateObj.gateNumber;
    const gName = gateObj.gateName || `Cổng ${gNum}`;
    const gProg = gateObj.progressPercent || 50;
    const isDone = gateObj.isCompleted || false;

    if (gNum >= currentHighestGate || (isDone && gNum >= 5)) {
      currentHighestGate = Math.max(currentHighestGate, gNum);
      updateGateStepper(currentHighestGate, gName, gProg, isDone, gateObj.completedGates);
      if (lastAnnouncedGate !== gNum) {
        lastAnnouncedGate = gNum;
        appendLiveStreamLine(
          time,
          "GATE",
          "term-gate",
          `[GATE ${gNum}] ${gName} (${gProg}%)`,
          "gate"
        );
      }
    }
  }

  // 1. Thinking / Suy nghĩ nội tâm của Agent
  if (ev.thought) {
    const preview = ev.thought.length > 250 ? ev.thought.slice(0, 250) + "..." : ev.thought;
    appendLiveStreamLine(
      time,
      "THINKING",
      "term-thought",
      preview,
      "thought"
    );
  }

  // 2. Tool Calls
  const toolList = ev.toolDetails || ev.tools;
  if (toolList && toolList.length > 0) {
    for (const tool of toolList) {
      const toolName = typeof tool === "string" ? tool : (tool.name || "tool");
      const summary = typeof tool === "object" ? (tool.summary || tool.command || toolName) : tool;
      appendLiveStreamLine(
        time,
        "TOOL",
        "term-tool",
        `${toolName}: ${summary}`,
        "tool"
      );
    }
  }

  // 3. User Input
  if (ev.type === "USER_INPUT") {
    appendLiveStreamLine(
      time,
      "USER",
      "term-user",
      ev.contentPreview || ev.content || "Yêu cầu sản xuất",
      "gate"
    );
  }
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

// ── TRỤC ĐỒNG BỘ 7 TRỤC: TASK QUEUE & INSPECTOR CONTROLLER ──
function openTaskQueueModal() {
  const modal = document.getElementById("task-queue-modal");
  if (modal) modal.classList.add("active");
  loadTaskQueue();
}

function closeTaskQueueModal() {
  const modal = document.getElementById("task-queue-modal");
  if (modal) modal.classList.remove("active");
}

async function loadTaskQueue() {
  const container = document.getElementById("task-queue-list");
  if (!container) return;

  try {
    const res = await fetch("/api/commander/tasks");
    const data = await res.json();
    if (data.success && data.queue) {
      const queue = data.queue;
      const badgeHeader = document.getElementById("queue-badge-count-header");
      const countFooter = document.getElementById("queue-footer-count");
      if (badgeHeader) badgeHeader.textContent = queue.length;
      if (countFooter) countFooter.textContent = queue.length;

      if (queue.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-xs font-mono text-gray-400">Hàng đợi đang trống. Sếp có thể dán link hoặc giao việc ở trên!</div>`;
        return;
      }

      container.innerHTML = queue.map(item => {
        let statusBadge = "";
        if (item.status === "completed") {
          statusBadge = `<span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">✓ HOÀN TẤT</span>`;
        } else if (item.status === "aborted") {
          statusBadge = `<span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">🛑 ĐÃ HỦY</span>`;
        } else if (item.status === "waiting_approval") {
          statusBadge = `<span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 animate-pulse">⏳ CHỜ DUYỆT</span>`;
        } else if (item.status === "running") {
          statusBadge = `<span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-pink-100 text-pink-700 animate-pulse">● ĐANG CHẠY</span>`;
        } else {
          statusBadge = `<span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">⏳ XẾP HÀNG</span>`;
        }

        const workshopBadge = `<span class="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-pink-50 text-pink-600 border border-pink-200 uppercase">${escapeHtml(item.workshop || 'threads')}</span>`;
        const pubTitle = item.artifacts?.publishingKit?.title;

        return `
          <div class="task-queue-card ${item.status}">
            <div class="flex items-start justify-between gap-3">
              ${item.status === 'completed' ? `
                <div class="w-14 h-20 rounded-xl overflow-hidden bg-gray-900 shrink-0 border border-pink-200 cursor-pointer shadow-xs hover:border-pink-500 transition-all group relative" onclick="openSeoKitModal('${item.id}')" title="Xem Thumbnail & AI SEO Kit">
                  <img src="${item.artifacts?.thumbUrl || `/media/${item.workshop || 'threads'}/${item.id}/thumb.jpg`}" class="w-full h-full object-cover" onerror="this.src='/media/threads/job_thread_hoangbao_ban_cung_ban/thumb.jpg'">
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                    <span class="material-symbols-outlined text-white text-xs">auto_awesome</span>
                  </div>
                </div>
              ` : ''}
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  ${workshopBadge}
                  ${statusBadge}
                  <span class="text-[10px] font-mono text-gray-400">${escapeHtml(item.id)}</span>
                </div>
                <div class="font-bold text-xs text-gray-800 line-clamp-1">${escapeHtml(item.title)}</div>
                ${pubTitle ? `<div class="text-[11px] font-sans font-semibold text-rose-600 mt-0.5 line-clamp-1 flex items-center gap-1"><span class="material-symbols-outlined text-[13px] text-pink-500">auto_awesome</span> ${escapeHtml(pubTitle)}</div>` : ''}
                <div class="text-[11px] font-mono text-pink-600 mt-0.5">${escapeHtml(item.gateName || 'Tiến trình 7 Cổng')}</div>
              </div>

              <!-- Action buttons on each task -->
              <div class="flex items-center gap-1.5 shrink-0">
                ${item.status === 'completed' ? `
                  <button type="button" class="px-2.5 py-1 rounded-lg bg-pink-100 hover:bg-pink-200 text-pink-700 text-xs font-bold transition-all flex items-center gap-1 cursor-pointer" onclick="openSeoKitModal('${item.id}')" title="Xem & Sinh Tiêu Đề, Caption, Mô Tả & Tags SEO">
                    <span class="material-symbols-outlined text-xs">auto_awesome</span> SEO Kit
                  </button>
                ` : ''}
                <button type="button" class="px-2.5 py-1 rounded-lg bg-pink-50 hover:bg-pink-100 text-pink-700 text-xs font-bold transition-all flex items-center gap-1 cursor-pointer" onclick="inspectTaskDetail('${item.id}')" title="Soi chi tiết toàn bộ thông tin & sản phẩm">
                  <span class="material-symbols-outlined text-xs">troubleshoot</span> Soi Job
                </button>
                ${item.status === 'completed' || item.status === 'aborted' ? `
                  <button type="button" class="p-1 rounded-lg text-gray-400 hover:text-pink-600 hover:bg-pink-50 transition-colors cursor-pointer" onclick="rerunTaskInQueue('${item.id}')" title="Chạy lại task này">
                    <span class="material-symbols-outlined text-sm">replay</span>
                  </button>
                ` : ''}
                <button type="button" class="p-1 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer" onclick="deleteTaskFromQueue('${item.id}')" title="Xóa task này">
                  <span class="material-symbols-outlined text-sm">delete</span>
                </button>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="w-full bg-pink-100/60 h-1 rounded-full overflow-hidden mt-1">
              <div class="bg-gradient-to-r from-pink-500 to-rose-500 h-full rounded-full transition-all duration-300" style="width: ${item.progress || 10}%"></div>
            </div>
          </div>
        `;
      }).join("");
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
    const res = await fetch("/api/commander/tasks/batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rawText: raw, workshop: "threads" })
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

async function deleteTaskFromQueue(id) {
  try {
    const res = await fetch(`/api/commander/tasks/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Đã xóa tác vụ khỏi hàng đợi!");
      loadTaskQueue();
    }
  } catch (err) {
    showToast("Lỗi xóa task: " + err.message, "error");
  }
}

async function clearTaskQueue(onlyCompleted) {
  try {
    const res = await fetch("/api/commander/tasks/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ onlyCompleted })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      loadTaskQueue();
    }
  } catch (err) {
    showToast("Lỗi dọn hàng đợi: " + err.message, "error");
  }
}

async function rerunTaskInQueue(id) {
  try {
    const res = await fetch(`/api/commander/tasks/${id}/rerun`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast("Đã nạp lại tác vụ vào hàng đợi!");
      loadTaskQueue();
    }
  } catch (err) {
    showToast("Lỗi nạp lại: " + err.message, "error");
  }
}

async function inspectTaskDetail(id) {
  try {
    const res = await fetch(`/api/commander/tasks/${id}/detail`);
    const data = await res.json();
    if (!data.success || !data.task) {
      showToast("Không tìm thấy chi tiết tác vụ!", "error");
      return;
    }
    const task = data.task;
    const linked = data.linkedJob;

    const modal = document.getElementById("task-detail-modal");
    if (!modal) return;

    document.getElementById("detail-task-title").textContent = task.title;
    document.getElementById("detail-task-sub").textContent = `ID: ${task.id} • Tạo lúc: ${new Date(task.createdAt).toLocaleString("vi-VN")}`;
    document.getElementById("detail-status-badge").textContent = (task.status || "queued").toUpperCase();
    document.getElementById("detail-gate-badge").textContent = task.gateName || `Cổng ${task.currentGate}`;
    document.getElementById("detail-workshop-badge").textContent = (task.workshop || "threads").toUpperCase();
    document.getElementById("detail-progress-badge").textContent = `${task.progress || 0}%`;

    // Assets Box
    const assetsBox = document.getElementById("detail-assets-box");
    let assetHtml = "";
    if (linked && linked.videoUrl) {
      assetHtml += `
        <div class="p-3 rounded-xl bg-pink-50/50 border border-pink-200">
          <div class="text-xs font-bold text-gray-800 mb-2">🎬 Video Thành Phẩm:</div>
          <video src="${linked.videoUrl}" controls class="w-full max-h-60 rounded-lg bg-black"></video>
        </div>
      `;
    }
    if (task.artifacts && task.artifacts.youtubeUrl) {
      assetHtml += `
        <a href="${task.artifacts.youtubeUrl}" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-600 text-white text-xs font-bold shadow-sm hover:bg-red-700">
          <span class="material-symbols-outlined text-xs">smart_display</span> Xem Trên YouTube (Unlisted)
        </a>
      `;
    }
    assetsBox.innerHTML = assetHtml || `<div class="text-xs font-mono text-gray-400 p-2.5 bg-pink-50/40 rounded-lg border border-pink-100">Chưa có file video hoàn chỉnh cho tác vụ này. Khi đạt Cổng 6/7, video sẽ xuất hiện ở đây.</div>`;

    // SEO Publishing Kit Box in Task Detail
    const seoBox = document.getElementById("detail-seo-box");
    const seoContent = document.getElementById("detail-seo-content");
    const btnOpenSeo = document.getElementById("btn-open-seo-from-detail");
    const pubKit = task.artifacts?.publishingKit;

    if (pubKit && seoContent) {
      if (seoBox) seoBox.classList.remove("hidden");
      seoContent.innerHTML = `
        <div class="font-bold text-gray-900 line-clamp-1">${escapeHtml(pubKit.title || task.title)}</div>
        <div class="text-[11px] text-gray-600 line-clamp-2">${escapeHtml(pubKit.description || "")}</div>
        <div class="flex flex-wrap gap-1 mt-1">
          ${(pubKit.tags || []).slice(0, 8).map(t => `<span class="bg-pink-100/70 text-pink-700 px-1.5 py-0.5 rounded text-[10px] font-mono">#${escapeHtml(t)}</span>`).join("")}
        </div>
      `;
      if (btnOpenSeo) {
        btnOpenSeo.onclick = () => {
          closeTaskDetailModal();
          openSeoKitModal(task.id);
        };
      }
    } else if (seoBox) {
      seoBox.classList.add("hidden");
    }

    // Logs
    const logsBox = document.getElementById("detail-task-logs");
    if (logsBox) {
      logsBox.innerHTML = (task.logs || ["Chưa có nhật ký"]).map(l => `<div>${escapeHtml(l)}</div>`).join("");
    }

    // Delete button wiring
    const delBtn = document.getElementById("btn-detail-delete");
    if (delBtn) {
      delBtn.onclick = () => {
        deleteTaskFromQueue(task.id);
        closeTaskDetailModal();
      };
    }

    modal.classList.add("active");
  } catch (err) {
    showToast("Lỗi mở chi tiết task: " + err.message, "error");
  }
}

function closeTaskDetailModal() {
  const modal = document.getElementById("task-detail-modal");
  if (modal) modal.classList.remove("active");
}

function renderHitlActionForWorkshop5(username) {
  const hitlActions = document.getElementById("leader-hitl-actions");
  if (!hitlActions) return;

  let btnW5 = document.getElementById("btn-dynamic-workshop-action");
  if (!btnW5) {
    btnW5 = document.createElement("button");
    btnW5.id = "btn-dynamic-workshop-action";
    btnW5.className = "px-3 py-1 rounded-lg bg-pink-500 text-white font-bold text-xs transition-all shadow-md flex items-center gap-1 animate-pulse hover:bg-pink-600 cursor-pointer";
    hitlActions.prepend(btnW5);
  }
  btnW5.innerHTML = `<span class="material-symbols-outlined text-xs">movie</span> ⚡ Bấm Máy Xưởng 5 Cho @${username} Ngay`;
  btnW5.disabled = false;
  btnW5.onclick = () => {
    btnW5.disabled = true;
    btnW5.innerHTML = `<span class="material-symbols-outlined text-xs animate-spin">sync</span> Đang Bấm Máy Xưởng 5...`;
    handleHitlAction("produce_threads");
    setTimeout(() => {
      const b = document.getElementById("btn-dynamic-workshop-action");
      if (b) b.remove();
    }, 6000);
  };
}

// 🛑 GLOBAL ABORT TRIGGER
async function triggerGlobalAbort() {
  if (!confirm("⚠️ Sếp có chắc chắn muốn DỪNG KHẨN CẤP toàn bộ tiến trình render và hàng đợi không?")) {
    return;
  }
  const abortBtn = document.getElementById("btn-global-abort");
  if (abortBtn) {
    abortBtn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>ĐANG HỦY...</span>`;
  }
  try {
    const res = await fetch("/api/commander/abort", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      appendLeaderLog("alert", `🛑 [SYSTEM ABORT] ${data.message}`);
      showToast("🛑 ĐÃ DỪNG KHẨN CẤP TOÀN BỘ TIẾN TRÌNH!", "error");
      
      // Reset Stepper to red aborted state
      for (let i = 1; i <= 7; i++) {
        const card = document.getElementById(`gate-card-${i}`);
        if (card && card.classList.contains("active")) {
          card.style.borderColor = "#ef4444";
        }
      }

      // Reset unified dispatch button
      const dispatchBtn = document.getElementById("btn-unified-dispatch");
      if (dispatchBtn) {
        dispatchBtn.disabled = false;
      }

      // Remove any active HITL action button
      const hitlDynamic = document.getElementById("btn-dynamic-workshop-action");
      if (hitlDynamic) hitlDynamic.remove();

      loadTaskQueue();
    }
  } catch (err) {
    showToast("Lỗi dừng khẩn cấp: " + err.message, "error");
  } finally {
    if (abortBtn) {
      abortBtn.innerHTML = `<span class="material-symbols-outlined text-[16px]">dangerous</span><span>DỪNG KHẨN CẤP</span>`;
    }
  }
}

// ── SINGLE SMART DISPATCH CONTROLLER LOGIC ──
let currentDispatchMode = "ai_leader";
let currentIntakeMode = "single";

function setDispatchMode(mode) {
  currentDispatchMode = mode;
  const pillAi = document.getElementById("mode-pill-ai");
  const pillLocal = document.getElementById("mode-pill-local");
  if (pillAi && pillLocal) {
    pillAi.classList.toggle("active", mode === "ai_leader");
    pillLocal.classList.toggle("active", mode === "local_worker");
  }
  const btnText = document.getElementById("btn-unified-dispatch-text");
  if (btnText) {
    if (currentIntakeMode === "batch") {
      btnText.textContent = "📋 Nạp Hàng Đợi & Bắt Đầu Sản Xuất";
    } else if (mode === "ai_leader") {
      btnText.textContent = "🚀 Bắt Đầu Sản Xuất Ngay (AI Leader)";
    } else {
      btnText.textContent = "⚡ Chạy Worker Cục Bộ Nhanh";
    }
  }
}

function setIntakeMode(mode) {
  currentIntakeMode = mode;
  const tabSingle = document.getElementById("tab-intake-single");
  const tabBatch = document.getElementById("tab-intake-batch");
  const singleBox = document.getElementById("intake-single-box");
  const batchBox = document.getElementById("intake-batch-box");
  const label = document.getElementById("label-intake-input");
  const btnText = document.getElementById("btn-unified-dispatch-text");

  if (mode === "batch") {
    if (tabSingle) tabSingle.className = "px-2.5 py-1 rounded-lg text-xs font-semibold text-gray-600 hover:text-pink-600 transition-all cursor-pointer";
    if (tabBatch) tabBatch.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-pink-500 text-white shadow-xs transition-all cursor-pointer";
    if (singleBox) singleBox.classList.add("hidden");
    if (batchBox) batchBox.classList.remove("hidden");
    if (label) label.textContent = "DÁN 5-10 LINK BÀI VIẾT HOẶC NHIỆM VỤ (MỖI DÒNG 1 VIỆC):";
    if (btnText) btnText.textContent = "📋 Nạp Toàn Bộ Vào Hàng Đợi & Bắt Đầu";
  } else {
    if (tabSingle) tabSingle.className = "px-2.5 py-1 rounded-lg text-xs font-bold bg-pink-500 text-white shadow-xs transition-all cursor-pointer";
    if (tabBatch) tabBatch.className = "px-2.5 py-1 rounded-lg text-xs font-semibold text-gray-600 hover:text-pink-600 transition-all cursor-pointer";
    if (singleBox) singleBox.classList.remove("hidden");
    if (batchBox) batchBox.classList.add("hidden");
    if (label) label.textContent = "DÁN LINK (THREADS / GITHUB) HOẶC GÕ LỆNH TIẾNG VIỆT TỰ NHIÊN:";
    if (btnText) btnText.textContent = currentDispatchMode === "ai_leader" ? "🚀 Bắt Đầu Sản Xuất Ngay (AI Leader)" : "⚡ Chạy Worker Cục Bộ Nhanh";
  }
}

function onWorkshopChange(workshop) {
  const ids = ["threads", "cinematic", "explainer", "whiteboard", "news"];
  ids.forEach(id => {
    const el = document.getElementById(`params-workshop-${id}`);
    if (el) {
      if (id === workshop) {
        el.classList.remove("hidden");
      } else {
        el.classList.add("hidden");
      }
    }
  });
}

function onModalWorkshopChange(ws) {
  // Can be expanded if modal has dynamic options
}

async function handleUnifiedDispatch() {
  const workshop = document.getElementById("dispatch-workshop")?.value || "threads";
  const autoPublish = document.getElementById("dispatch-publish")?.checked ?? true;
  const btn = document.getElementById("btn-unified-dispatch");

  if (currentIntakeMode === "batch") {
    const textarea = document.getElementById("leader-batch-textarea");
    const rawText = textarea?.value?.trim() || "";
    if (!rawText) {
      showToast("Vui lòng dán ít nhất 1 link hoặc nhiệm vụ!", "warning");
      return;
    }
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> <span>Đang nạp hàng đợi...</span>`;
    }
    try {
      const res = await fetch("/api/commander/tasks/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rawText, workshop, mode: currentDispatchMode })
      });
      const data = await res.json();
      if (data.success) {
        textarea.value = "";
        showToast(`Đã nạp ${data.count} tác vụ vào Hàng Đợi tự hành!`);
        openTaskQueueModal();
      }
    } catch (err) {
      showToast("Lỗi nạp hàng đợi: " + err.message, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">rocket_launch</span> <span>📋 Nạp Toàn Bộ Vào Hàng Đợi & Bắt Đầu</span>`;
      }
    }
    return;
  }

  // Single Input Mode
  const input = document.getElementById("leader-command-input");
  const cmd = input?.value?.trim() || "";
  if (!cmd) {
    showToast("Vui lòng nhập link bài viết hoặc yêu cầu kịch bản!", "warning");
    return;
  }

  // Omni-NLP Router: detect workshop and parameters
  const lower = cmd.toLowerCase();
  let detectedWorkshop = workshop;
  if (lower.includes("threads.net") || lower.includes("threads.com") || lower.includes("drama") || lower.includes("tâm sự")) {
    detectedWorkshop = "threads";
  } else if (lower.includes("github.com") || lower.includes("repo") || lower.includes("remotion") || lower.includes("code")) {
    detectedWorkshop = "explainer";
  } else if (lower.includes("3d") || lower.includes("donghua") || lower.includes("tiên hiệp") || lower.includes("chibi")) {
    detectedWorkshop = "cinematic";
  } else if (lower.includes("bảng trắng") || lower.includes("whiteboard") || lower.includes("vẽ tay")) {
    detectedWorkshop = "whiteboard";
  } else if (lower.includes("tin tức") || lower.includes("thời sự") || lower.includes("news")) {
    detectedWorkshop = "news";
  }

  const wsSelect = document.getElementById("dispatch-workshop");
  if (wsSelect && wsSelect.value !== detectedWorkshop) {
    wsSelect.value = detectedWorkshop;
    onWorkshopChange(detectedWorkshop);
  }

  // Visual feedback badge
  const badge = document.getElementById("nlp-feedback-badge");
  if (badge) {
    badge.classList.remove("hidden");
    badge.textContent = `✓ Đã nhận diện: Xưởng ${detectedWorkshop.toUpperCase()}`;
    setTimeout(() => badge.classList.add("hidden"), 4000);
  }

  // Gather parameters
  const bg = document.getElementById("dispatch-bg")?.value || "minecraft_parkour.mp4";
  const speed = document.getElementById("dispatch-speed")?.value || "1.25";

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> <span>Đang khởi động...</span>`;
  }

  try {
    if (currentDispatchMode === "ai_leader") {
      appendLeaderLog("thinking", `Giao việc cho AI Leader IDE 2.0: "${cmd}"`);
      const res = await fetch("/api/antigravity/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: cmd, workshop: detectedWorkshop, background: bg, speed, autoPublish })
      });
      const data = await res.json();
      if (data.success) {
        showToast("Đã giao việc cho AI Leader IDE 2.0!");
        appendLeaderLog("dispatch", "AI Leader đã tiếp nhận lệnh và kích hoạt 7 Cổng Sản Xuất.");
        loadTaskQueue();
      } else {
        showToast("Lỗi giao việc IDE 2.0: " + data.error, "error");
      }
    } else {
      appendLeaderLog("thinking", `Khởi động worker cục bộ cho lệnh: "${cmd}"`);
      const res = await fetch("/api/commander/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd, workshop: detectedWorkshop })
      });
      const data = await res.json();
      if (data.success) {
        showToast("Worker cục bộ đã tiếp nhận và bắt đầu xử lý!");
        if (data.type === "threads" && data.data) {
          const uName = data.data.thread_data?.post?.username || "threads_user";
          appendLeaderLog("radar", `Đã cào bài viết của @${uName}! Sẵn sàng bấm máy.`);
          renderHitlActionForWorkshop5(uName);
        }
        loadTaskQueue();
      } else {
        showToast("Lỗi worker: " + data.error, "error");
      }
    }
  } catch (err) {
    showToast("Lỗi kết nối: " + err.message, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">rocket_launch</span> <span id="btn-unified-dispatch-text">${currentDispatchMode === 'ai_leader' ? '🚀 Bắt Đầu Sản Xuất Ngay (AI Leader)' : '⚡ Chạy Worker Cục Bộ Nhanh'}</span>`;
    }
  }
}
// ── DATA LOADING & STATS ──
async function loadVideos() {
  try {
    const res = await fetch("/api/videos");
    const data = await res.json();
    if (data.success) {
      allVideos = data.videos || [];
      updateCategoryBadges();
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
              <button class="btn btn-sm btn-outline" onclick="openSeoKitModal('${v.id}')" title="Xem & Sinh Bộ Tiêu Đề, Caption, Mô Tả & Tags SEO">
                  ✨ SEO Kit
                </button>
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
                <button class="btn btn-sm btn-outline" onclick="openSeoKitModal('${v.id}')" title="Xem & Sinh Bộ Tiêu Đề, Caption, Mô Tả & Tags SEO">
                  ✨ SEO Kit
                </button>
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
            renderHitlActionForWorkshop5(p.username);
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
  let defaultTitle = (video.publishingKit && video.publishingKit.title) ? video.publishingKit.title : video.title;
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
  let desc = video.publishingKit?.description || `${video.title}\n\nSản xuất tự hành bởi OmniVideo Studio (Phân xưởng ${video.workshop.toUpperCase()})\n\n`;
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

// ── PLAY VIDEO MODAL (STITCH MCP CINEMATIC THEATER) ──
function closePlayerModal() {
  const modal = document.getElementById("player-modal");
  if (modal) {
    modal.classList.remove("active");
  }
  document.body.style.overflow = "";
  const vid = document.getElementById("main-video");
  if (vid) {
    vid.pause();
  }
}

function formatPlayerTime(seconds) {
  if (!seconds || isNaN(seconds)) return "00:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

function extractVideoChapters(video) {
  if (video.beats && video.beats.length > 0) {
    return video.beats.map((b, idx) => ({
      timeSec: idx * 4,
      timeStr: formatPlayerTime(idx * 4),
      speaker: b.speaker || "Narrator",
      role: b.role || "beat",
      text: b.rawText || b.text || ""
    }));
  }

  const desc = (video.publishingKit && video.publishingKit.description) || video.description || "";
  const lines = desc.split(/\r?\n/);
  const chapters = [];
  const chapRegex = /^(\d{1,2}):(\d{2})\s*[-–—:]\s*(.+)$/;

  lines.forEach(l => {
    const m = l.trim().match(chapRegex);
    if (m) {
      const min = parseInt(m[1], 10);
      const sec = parseInt(m[2], 10);
      const totalSec = min * 60 + sec;
      chapters.push({
        timeSec: totalSec,
        timeStr: String(min).padStart(2, "0") + ":" + String(sec).padStart(2, "0"),
        speaker: "Chapter " + (chapters.length + 1),
        role: "Mốc cảnh",
        text: m[3].trim()
      });
    }
  });

  if (chapters.length > 0) return chapters;

  // Fallback: extract comments if present
  const commentRegex = /^[•\-*]\s*@?([^:]+):\s*["“]?([^"”]+)["”]?$/;
  let commentIdx = 0;
  lines.forEach(l => {
    const m = l.trim().match(commentRegex);
    if (m) {
      commentIdx++;
      const estSec = (commentIdx - 1) * 6;
      chapters.push({
        timeSec: estSec,
        timeStr: formatPlayerTime(estSec),
        speaker: "@" + m[1].trim(),
        role: "Bình luận",
        text: m[2].trim()
      });
    }
  });

  return chapters;
}

let playerTimeListenersBound = false;

function initPlayerTimeListeners() {
  if (playerTimeListenersBound) return;
  const vid = document.getElementById("main-video");
  if (!vid) return;

  vid.addEventListener("timeupdate", () => {
    const curTime = document.getElementById("player-time-current");
    const durTime = document.getElementById("player-time-duration");
    const pBar = document.getElementById("player-progress-bar");
    const pPip = document.getElementById("player-scrub-pip");
    const shotLabel = document.getElementById("player-time-shot-label");

    if (curTime) curTime.textContent = formatPlayerTime(vid.currentTime);
    if (durTime && vid.duration) durTime.textContent = formatPlayerTime(vid.duration);

    if (vid.duration && vid.duration > 0) {
      const pct = Math.min(100, Math.max(0, (vid.currentTime / vid.duration) * 100));
      if (pBar) pBar.style.width = pct + "%";
      if (pPip) pPip.style.left = pct + "%";
    }

    if (shotLabel && currentPlayerVideoId) {
      const video = allVideos.find(v => v.id === currentPlayerVideoId);
      if (video) {
        const chapters = extractVideoChapters(video);
        if (chapters.length > 0) {
          let activeChap = chapters[0];
          for (let i = 0; i < chapters.length; i++) {
            if (vid.currentTime >= chapters[i].timeSec) {
              activeChap = chapters[i];
            } else {
              break;
            }
          }
          shotLabel.textContent = activeChap.speaker + ": " + (activeChap.text.length > 28 ? activeChap.text.slice(0, 28) + "..." : activeChap.text);
        }
      }
    }
  });

  vid.addEventListener("loadedmetadata", () => {
    const durTime = document.getElementById("player-time-duration");
    const durEl = document.getElementById("player-telemetry-duration");
    const resSpec = document.getElementById("player-res-spec");

    if (durTime && vid.duration) durTime.textContent = formatPlayerTime(vid.duration);
    if (durEl && vid.duration) {
      const video = allVideos.find(v => v.id === currentPlayerVideoId);
      const count = video ? extractVideoChapters(video).length : 0;
      durEl.textContent = formatPlayerTime(vid.duration) + " (" + count + " Phân Cảnh)";
    }
    if (resSpec && vid.videoWidth && vid.videoHeight) {
      resSpec.textContent = vid.videoWidth + "x" + vid.videoHeight;
    }
  });

  vid.addEventListener("play", () => {
    const playIcon = document.getElementById("player-play-icon");
    const bigPlayBtn = document.getElementById("player-big-play-btn");
    if (playIcon) playIcon.textContent = "pause";
    if (bigPlayBtn) bigPlayBtn.style.opacity = "0";
  });

  vid.addEventListener("pause", () => {
    const playIcon = document.getElementById("player-play-icon");
    const bigPlayBtn = document.getElementById("player-big-play-btn");
    if (playIcon) playIcon.textContent = "play_arrow";
    if (bigPlayBtn) bigPlayBtn.style.opacity = "1";
  });

  vid.addEventListener("ended", () => {
    const playIcon = document.getElementById("player-play-icon");
    const bigPlayBtn = document.getElementById("player-big-play-btn");
    if (playIcon) playIcon.textContent = "replay";
    if (bigPlayBtn) bigPlayBtn.style.opacity = "1";
  });

  playerTimeListenersBound = true;
}

function openPlayer(jobId) {
  currentPlayerVideoId = jobId;
  const video = allVideos.find(v => v.id === jobId);
  if (!video) {
    showToast("Không tìm thấy dữ liệu video: " + jobId, "warning");
    return;
  }

  initPlayerTimeListeners();

  const titleEl = document.getElementById("modal-video-title");
  if (titleEl) titleEl.textContent = video.title || jobId;

  const badgeEl = document.getElementById("modal-workshop-badge");
  if (badgeEl) {
    const wsNames = {
      threads: "✦ THREADS SOCIAL DRAMA (9:16)",
      cinematic: "✦ PHIM ĐIỆN ẢNH 3D (16:9)",
      whiteboard: "✦ WHITEBOARD DRAMA",
      news: "✦ TIN TỨC HYPERFRAMES",
      explainer: "✦ REMOTION EXPLAINER"
    };
    badgeEl.textContent = wsNames[video.workshop] || ("✦ " + video.workshop.toUpperCase());
  }

  // Set adaptive aspect ratio: 9:16 for threads/news, 16:9 for cinematic/others
  const isPortrait = video.workshop === "threads" || video.workshop === "news" || (video.metadata && video.metadata.aspect === "9:16");
  setPlayerAspectRatio(isPortrait ? "9:16" : "16:9");

  // Video source
  const vid = document.getElementById("main-video");
  const btnDownloadMp4 = document.getElementById("btn-download-mp4");
  if (vid) {
    if (video.videoUrl) {
      vid.src = video.videoUrl;
      vid.load();
      if (btnDownloadMp4) {
        btnDownloadMp4.href = video.videoUrl;
        btnDownloadMp4.setAttribute("download", jobId + ".mp4");
        btnDownloadMp4.style.display = "inline-flex";
      }
    } else {
      vid.src = "";
      if (btnDownloadMp4) btnDownloadMp4.style.display = "none";
    }
  }

  // Telemetry data
  const sizeEl = document.getElementById("player-telemetry-size");
  if (sizeEl) {
    const sizeBytes = video.sizeBytes || video.fileSizeBytes || video.size || 0;
    sizeEl.textContent = formatBytes(sizeBytes);
  }

  const durEl = document.getElementById("player-telemetry-duration");
  const chapters = extractVideoChapters(video);
  if (durEl) {
    durEl.textContent = (video.duration || "00:45") + " (" + chapters.length + " Phân Cảnh)";
  }

  const voiceEl = document.getElementById("player-telemetry-voice");
  if (voiceEl) {
    voiceEl.textContent = video.voiceId ? (video.voiceId + " (Rate +25%)") : "vi-VN-NamMinhNeural (Rate +25%)";
  }

  const captionEl = document.getElementById("player-caption-snippet");
  if (captionEl) {
    const descFirstLine = video.publishingKit && video.publishingKit.description ? video.publishingKit.description.split("\n")[0] : null;
    captionEl.textContent = descFirstLine || video.caption || video.description || video.title || "Khám phá nội dung câu chuyện xuất bản tự hành bởi OmniVideo Studio...";
  }

  // Chapter Timeline
  const timelineEl = document.getElementById("beats-timeline");
  const beatsBadge = document.getElementById("beats-count-badge");
  if (beatsBadge) {
    beatsBadge.textContent = chapters.length + " phân đoạn";
  }

  if (timelineEl) {
    if (chapters.length === 0) {
      timelineEl.innerHTML = '<div class="p-3 rounded-xl bg-white/5 text-center text-xs text-slate-400">Chưa có danh sách Phân Cảnh cho video này.</div>';
    } else {
      timelineEl.innerHTML = chapters.map((chap, idx) => {
        const estTime = chap.timeStr;
        const role = escapeHtml(chap.role);
        const speaker = escapeHtml(chap.speaker);
        const text = escapeHtml(chap.text);
        return '<div class="p-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-pink-500/30 transition-all cursor-pointer group flex items-start gap-2.5" onclick="seekVideoBeat(' + idx + ', ' + chap.timeSec + ')">' +
          '<span class="px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-300 text-[10px] font-mono font-bold shrink-0 mt-0.5">' + estTime + '</span>' +
          '<div class="min-w-0 flex-1">' +
            '<div class="flex items-center gap-1.5 text-[11px]">' +
              '<span class="font-bold text-slate-200 group-hover:text-pink-300 transition-colors">' + speaker + '</span>' +
              '<span class="text-[9px] px-1 rounded bg-white/10 text-slate-400 font-mono">' + role + '</span>' +
            '</div>' +
            '<div class="text-[11px] text-slate-400 truncate mt-0.5">' + text + '</div>' +
          '</div>' +
          '<span class="material-symbols-outlined text-slate-500 group-hover:text-pink-400 text-sm shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity">play_circle</span>' +
        '</div>';
      }).join("");
    }
  }

  const modal = document.getElementById("player-modal");
  if (modal) {
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }
}

function seekVideoBeat(index, targetSec) {
  const vid = document.getElementById("main-video");
  if (vid) {
    if (typeof targetSec === "number" && targetSec >= 0) {
      vid.currentTime = Math.min(vid.duration || 9999, targetSec);
    } else if (vid.duration) {
      vid.currentTime = Math.min(vid.duration, index * 4);
    }
    vid.play().catch(() => {});
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
        fetch("/api/commander/tasks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            jobId: data.jobId,
            title,
            workshop,
            status: "running",
            currentGate: 1,
            gateName: "Cổng 1: Bóc Tách Kịch Bản Mới",
            progress: 20,
            mode: "ai_leader",
            params: { voiceId, rawPrompt: rawContent },
            logs: [`[${new Date().toLocaleTimeString("vi-VN")}] Khởi tạo từ Modal Tạo Video Mới. Bắt đầu render!`]
          })
        }).then(() => loadTaskQueue()).catch(() => {});
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
  initAntigravityBridge();
  loadVideos().then(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const autoPlayerId = urlParams.get("openPlayer");
    if (autoPlayerId) {
      setTimeout(() => openPlayer(autoPlayerId), 250);
    }
  });
  loadTaskQueue();
});


// =========================================================================
// 🌸 SEO & PUBLISHING KIT CONTROLLER (STUDIO GENERATOR)
// =========================================================================
let currentSeoTaskId = null;
let currentSeoKitData = null;

async function openSeoKitModal(id) {
  currentSeoTaskId = id;
  const modal = document.getElementById("seo-kit-modal");
  if (!modal) return;

  try {
    let task = null;
    let kit = null;
    const res = await fetch(`/api/commander/tasks/${encodeURIComponent(id)}/detail`);
    const data = await res.json();
    if (data.success && data.task) {
      task = data.task;
      kit = task.artifacts?.publishingKit;
    }

    if (!kit) {
      const vid = allVideos.find(v => v.id === id);
      if (vid && vid.publishingKit) {
        kit = vid.publishingKit;
      }
    }

    if (!kit) {
      showToast("Đang sinh bộ Tiêu đề, Caption & SEO bằng AI...", "info");
      const genRes = await fetch(`/api/commander/tasks/${encodeURIComponent(id)}/generate-seo`, { method: "POST" });
      const genData = await genRes.json();
      if (genData.success && genData.publishingKit) {
        kit = genData.publishingKit;
      }
    }

    if (!kit) {
      kit = {
        title: task ? task.title : id,
        title_options: [task ? task.title : id],
        description: "Video sản xuất tự hành bởi OmniVideo Studio.\n\n#OmniVideo #Shorts #Threads",
        tags: ["OmniVideo", "Shorts", "Viral", "Threads"]
      };
    }

    currentSeoKitData = kit;

    // --- THUMBNAIL STUDIO INTEGRATION ---
    const thumbImg = document.getElementById("seo-thumb-preview");
    const thumbDl = document.getElementById("seo-thumb-download-link");
    const thumbOpen = document.getElementById("seo-thumb-open-link");
    const thumbRes = document.getElementById("seo-thumb-res-pill");

    const workshop = (task?.workshop || "threads").toLowerCase();
    const isPortrait = workshop === "threads";
    if (thumbRes) thumbRes.textContent = isPortrait ? "1080x1920" : "1920x1080";

    let thumbUrl = task?.artifacts?.thumbUrl || (task ? `/media/${workshop}/${task.id}/thumb.jpg` : "");
    if (!thumbUrl) {
      const vid = allVideos.find(v => v.id === id);
      if (vid) thumbUrl = vid.thumbUrl;
    }

    if (thumbImg) {
      thumbImg.src = thumbUrl ? `${thumbUrl}${thumbUrl.includes('?') ? '&' : '?'}t=${Date.now()}` : "";
      thumbImg.onerror = () => {
        // Fallback to demo existing thumb if task thumb is not yet on disk
        thumbImg.src = "/media/threads/job_thread_hoangbao_ban_cung_ban/thumb.jpg";
      };
    }
    if (thumbDl) thumbDl.href = thumbUrl || "#";
    if (thumbOpen) thumbOpen.href = thumbUrl || "#";

    const hookInput = document.getElementById("seo-thumb-hook-input");
    if (hookInput) {
      let hook = kit.hook_text;
      if (!hook && (kit.title || task?.title)) {
        const rawT = kit.title || task.title;
        const clean = rawT.replace(/^[🔥⚡🚨s]+/, '').split(/[...:?!#-]/)[0].trim();
        hook = clean.split(' ').slice(0, 5).join(' ');
      }
      hookInput.value = hook || "VIRAL THREADS 2026";
    }

    loadSeoFrameCandidates(id);
    // --- END THUMBNAIL STUDIO INTEGRATION ---

    const titlePill = document.getElementById("seo-workshop-pill");
    if (titlePill) titlePill.textContent = (task?.workshop || "threads").toUpperCase();

    const titleInput = document.getElementById("seo-title-input");
    const titleCount = document.getElementById("seo-title-count");
    if (titleInput) {
      titleInput.value = kit.title || "";
      if (titleCount) titleCount.textContent = `${titleInput.value.length} / 100`;
      titleInput.oninput = () => {
        if (titleCount) titleCount.textContent = `${titleInput.value.length} / 100`;
      };
    }

    const optionsList = document.getElementById("seo-title-options-list");
    if (optionsList) {
      const opts = kit.title_options || [kit.title];
      optionsList.innerHTML = opts.map(opt => `
        <div class="p-2 rounded-xl bg-pink-50/60 hover:bg-pink-100 border border-pink-100 text-xs text-gray-800 cursor-pointer flex items-center justify-between group transition-all" onclick="selectTitleOption('${escapeHtml(opt).replace(/'/g, "\\'")}')">
          <span class="line-clamp-1 font-semibold">${escapeHtml(opt)}</span>
          <span class="text-[10px] text-pink-600 font-bold bg-white px-2 py-0.5 rounded-full border border-pink-200 opacity-80 group-hover:opacity-100 transition-opacity">Chọn tiêu đề này ↵</span>
        </div>
      `).join("");
    }

    const captionInput = document.getElementById("seo-caption-input");
    if (captionInput) {
      captionInput.value = kit.caption || (kit.description ? kit.description.slice(0, 250) : "");
    }

    const descInput = document.getElementById("seo-desc-input");
    if (descInput) {
      descInput.value = kit.description || "";
    }

    const tagsInput = document.getElementById("seo-tags-input");
    const tagsChips = document.getElementById("seo-tags-chips");
    const tagsArray = Array.isArray(kit.tags) ? kit.tags : (kit.tags ? kit.tags.split(",").map(s => s.trim()) : []);
    if (tagsInput) {
      tagsInput.value = tagsArray.join(", ");
    }
    if (tagsChips) {
      tagsChips.innerHTML = tagsArray.map(t => `<span class="bg-pink-100/80 text-pink-700 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold">#${escapeHtml(t)}</span>`).join("");
    }

    modal.classList.add("active");
  } catch (err) {
    showToast("Lỗi mở SEO Kit: " + err.message, "error");
  }
}

function closeSeoKitModal() {
  const modal = document.getElementById("seo-kit-modal");
  if (modal) modal.classList.remove("active");
}

function selectTitleOption(title) {
  const titleInput = document.getElementById("seo-title-input");
  const titleCount = document.getElementById("seo-title-count");
  if (titleInput) {
    titleInput.value = title;
    if (titleCount) titleCount.textContent = `${title.length} / 100`;
    showToast("Đã áp dụng tiêu đề mới!");
  }
}

function copySeoField(fieldId, name) {
  const el = document.getElementById(fieldId);
  if (!el || !el.value) return;
  navigator.clipboard.writeText(el.value).then(() => {
    showToast(`Đã copy ${name} vào bộ nhớ tạm!`, "success");
  }).catch(() => {
    el.select();
    document.execCommand("copy");
    showToast(`Đã copy ${name}!`, "success");
  });
}

function copyFullPublishingKit() {
  const title = document.getElementById("seo-title-input")?.value || "";
  const caption = document.getElementById("seo-caption-input")?.value || "";
  const desc = document.getElementById("seo-desc-input")?.value || "";
  const tags = document.getElementById("seo-tags-input")?.value || "";

  const fullText = `=== TIÊU ĐỀ HIGH-CTR ===\n${title}\n\n=== CAPTION MẠNG XÃ HỘI ===\n${caption}\n\n=== MÔ TẢ YOUTUBE ===\n${desc}\n\n=== TAGS SEO ===\n${tags}`;
  navigator.clipboard.writeText(fullText).then(() => {
    showToast("Đã copy toàn bộ Bộ Publishing Kit!", "success");
  });
}

async function triggerRegenerateSeo() {
  if (!currentSeoTaskId) return;
  const btn = document.getElementById("btn-regenerate-seo");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> <span>Đang sinh lại...</span>`;
  }
  try {
    const res = await fetch(`/api/commander/tasks/${encodeURIComponent(currentSeoTaskId)}/generate-seo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ regenerate: true })
    });
    const data = await res.json();
    if (data.success && data.publishingKit) {
      showToast("Đã tái tạo bộ Tiêu đề & SEO thành công!", "success");
      openSeoKitModal(currentSeoTaskId);
      loadTaskQueue();
      loadVideos();
    }
  } catch (err) {
    showToast("Lỗi sinh SEO: " + err.message, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">refresh</span> <span>Tạo Lại Bằng AI</span>`;
    }
  }
}

async function saveSeoKitChanges() {
  if (!currentSeoTaskId) return;
  const title = document.getElementById("seo-title-input")?.value || "";
  const caption = document.getElementById("seo-caption-input")?.value || "";
  const description = document.getElementById("seo-desc-input")?.value || "";
  const rawTags = document.getElementById("seo-tags-input")?.value || "";
  const tags = rawTags.split(",").map(t => t.trim()).filter(Boolean);

  const updatedKit = {
    ...currentSeoKitData,
    title,
    caption,
    description,
    tags
  };

  try {
    await fetch(`/api/commander/tasks/${encodeURIComponent(currentSeoTaskId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        artifacts: {
          publishingKit: updatedKit,
          title,
          caption,
          tags
        }
      })
    });
    showToast("Đã lưu bộ Publishing Kit thành công!", "success");
    closeSeoKitModal();
    loadTaskQueue();
    loadVideos();
  } catch (err) {
    showToast("Lỗi lưu SEO Kit: " + err.message, "error");
  }
}

function transferSeoToYouTubeModal() {
  const title = document.getElementById("seo-title-input")?.value || "";
  const description = document.getElementById("seo-desc-input")?.value || "";
  const tags = document.getElementById("seo-tags-input")?.value || "";

  closeSeoKitModal();
  openYouTubeUploadModal(currentSeoTaskId);

  setTimeout(() => {
    const ytTitle = document.getElementById("yt-title");
    const ytDesc = document.getElementById("yt-description");
    const ytTags = document.getElementById("yt-tags");
    const ytCounter = document.getElementById("yt-title-counter");

    if (ytTitle && title) {
      ytTitle.value = title.slice(0, 100);
      if (ytCounter) ytCounter.textContent = `${ytTitle.value.length} / 100`;
    }
    if (ytDesc && description) ytDesc.value = description;
    if (ytTags && tags) ytTags.value = tags;
    showToast("Đã chuyển toàn bộ dữ liệu SEO sang YouTube Uploader!", "success");
  }, 200);
}

async function generateAllSeoKits() {
  showToast("Đang quét và sinh SEO Kit cho toàn bộ task hoàn tất...", "info");
  try {
    const res = await fetch("/api/commander/tasks/generate-all-seo", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || `Đã sinh xong SEO cho ${data.count} task!`, "success");
      loadTaskQueue();
      loadVideos();
    }
  } catch (err) {
    showToast("Lỗi sinh SEO hàng loạt: " + err.message, "error");
  }
}


// =============================================================================
// 🎨 THUMBNAIL STUDIO & HIGH-CTR GENERATOR CONTROLLER
// =============================================================================
async function loadSeoFrameCandidates(id) {
  const list = document.getElementById("seo-frame-candidates-list");
  const loader = document.getElementById("seo-thumb-loading-frames");
  if (!list) return;

  if (loader) loader.classList.remove("hidden");
  try {
    const res = await fetch(`/api/commander/tasks/${encodeURIComponent(id)}/frames`);
    const data = await res.json();
    if (data.success && Array.isArray(data.frames) && data.frames.length > 0) {
      list.innerHTML = data.frames.map(f => `
        <div class="relative aspect-[9/16] rounded-xl overflow-hidden border border-pink-200 hover:border-pink-500 cursor-pointer group shadow-xs transition-all bg-gray-900" onclick="selectSeoCandidateFrame('${escapeHtml(f.filename)}', '${escapeHtml(f.url)}')">
          <img src="${f.url}" class="w-full h-full object-cover group-hover:scale-105 transition-transform" />
          <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/75 text-[9px] font-mono text-white font-bold">${escapeHtml(f.name)}</span>
          <div class="absolute inset-0 bg-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <span class="material-symbols-outlined text-white text-base">check_circle</span>
          </div>
        </div>
      `).join("");
    } else {
      list.innerHTML = `<span class="col-span-4 text-[10px] font-mono text-gray-400 p-2">Chưa có frame candidate dự phòng. Bấm 📸 để trích frame!</span>`;
    }
  } catch (_) {
    list.innerHTML = `<span class="col-span-4 text-[10px] font-mono text-gray-400 p-2">Không thể tải danh sách frame.</span>`;
  } finally {
    if (loader) loader.classList.add("hidden");
  }
}

async function triggerGenerateHighCtrThumbnail() {
  if (!currentSeoTaskId) return;
  const btn = document.getElementById("btn-generate-thumb");
  const hookInput = document.getElementById("seo-thumb-hook-input");
  const hookText = hookInput?.value?.trim() || "";

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> <span>Đang Sinh...</span>`;
  }

  try {
    const res = await fetch(`/api/commander/tasks/${encodeURIComponent(currentSeoTaskId)}/generate-thumbnail`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hookText })
    });
    const data = await res.json();
    if (data.success) {
      showToast("✨ Đã sinh Thumbnail High-CTR thành công!", "success");
      const thumbImg = document.getElementById("seo-thumb-preview");
      const thumbDl = document.getElementById("seo-thumb-download-link");
      const thumbOpen = document.getElementById("seo-thumb-open-link");
      const freshUrl = `${data.thumbUrl}${data.thumbUrl.includes('?') ? '&' : '?'}t=${Date.now()}`;
      if (thumbImg) thumbImg.src = freshUrl;
      if (thumbDl) thumbDl.href = data.thumbUrl;
      if (thumbOpen) thumbOpen.href = data.thumbUrl;
      loadTaskQueue();
      loadVideos();
    } else {
      showToast("Lỗi sinh thumbnail: " + (data.error || "Thất bại"), "error");
    }
  } catch (err) {
    showToast("Lỗi kết nối sinh thumbnail: " + err.message, "error");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">auto_awesome</span> <span>Sinh Thumbnail High-CTR</span>`;
    }
  }
}

async function selectSeoCandidateFrame(filename, url) {
  if (!currentSeoTaskId) return;
  showToast("Đang áp dụng frame làm nền thumbnail...", "info");
  try {
    const hookText = document.getElementById("seo-thumb-hook-input")?.value?.trim() || "";
    const res = await fetch(`/api/commander/tasks/${encodeURIComponent(currentSeoTaskId)}/generate-thumbnail`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hookText, frameCandidate: filename })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Đã đổi frame nền & cập nhật Thumbnail!", "success");
      const thumbImg = document.getElementById("seo-thumb-preview");
      const thumbDl = document.getElementById("seo-thumb-download-link");
      const freshUrl = `${data.thumbUrl}${data.thumbUrl.includes('?') ? '&' : '?'}t=${Date.now()}`;
      if (thumbImg) thumbImg.src = freshUrl;
      if (thumbDl) thumbDl.href = data.thumbUrl;
      loadTaskQueue();
      loadVideos();
    } else {
      showToast("Lỗi đổi frame: " + (data.error || "Thất bại"), "error");
    }
  } catch (err) {
    showToast("Lỗi chọn frame: " + err.message, "error");
  }
}

function downloadCurrentThumbnail() {
  const preview = document.getElementById("seo-thumb-preview");
  if (!preview || !preview.src) {
    showToast("Không tìm thấy ảnh thumbnail để tải!", "warning");
    return;
  }
  const link = document.createElement("a");
  link.href = preview.src;
  link.download = `thumbnail_${currentSeoTaskId || 'video'}.jpg`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast("Đang tải thumbnail về máy...", "success");
}

async function extractFreshFramesForSeo() {
  if (!currentSeoTaskId) return;
  showToast("Đang trích xuất các frame mới từ video...", "info");
  try {
    const res = await fetch("/api/video/extract-frames", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jobId: currentSeoTaskId })
    });
    const data = await res.json();
    if (data.success && data.frames) {
      showToast("Đã trích xuất xong các frame từ video!", "success");
      loadSeoFrameCandidates(currentSeoTaskId);
    } else {
      showToast("Lỗi trích xuất frame: " + (data.error || "Không thành công"), "error");
    }
  } catch (err) {
    showToast("Lỗi kết nối trích xuất: " + err.message, "error");
  }
}


// =============================================================================
// 🎬 STITCH CINEMATIC THEATER PLAYER CONTROLLER
// =============================================================================
let currentPlayerVideoId = null;

function setPlayerAspectRatio(aspect) {
  const stage = document.getElementById("player-stage-box");
  const btnV = document.getElementById("player-aspect-btn-vertical");
  const btnH = document.getElementById("player-aspect-btn-horizontal");
  const resSpec = document.getElementById("player-res-spec");

  if (!stage) return;
  if (aspect === "9:16") {
    stage.className = "relative h-full max-h-[500px] aspect-[9/16] rounded-2xl overflow-hidden border border-white/20 bg-black shadow-[0_0_50px_rgba(0,194,224,0.15)] group flex items-center justify-center transition-all duration-300";
    if (btnV) {
      btnV.className = "px-3 py-1 rounded-full bg-pink-600 text-white font-bold shadow-[0_0_12px_rgba(219,41,101,0.4)] flex items-center gap-1.5 transition-all cursor-pointer";
    }
    if (btnH) {
      btnH.className = "px-3 py-1 rounded-full text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer";
    }
    if (resSpec) resSpec.textContent = "1080x1920";
  } else {
    stage.className = "relative h-full max-h-[500px] aspect-video rounded-2xl overflow-hidden border border-white/20 bg-black shadow-[0_0_50px_rgba(0,194,224,0.15)] group flex items-center justify-center transition-all duration-300";
    if (btnH) {
      btnH.className = "px-3 py-1 rounded-full bg-cyan-600 text-white font-bold shadow-[0_0_12px_rgba(0,194,224,0.4)] flex items-center gap-1.5 transition-all cursor-pointer";
    }
    if (btnV) {
      btnV.className = "px-3 py-1 rounded-full text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors cursor-pointer";
    }
    if (resSpec) resSpec.textContent = "1920x1080";
  }
}

function playerTogglePlay() {
  const vid = document.getElementById("main-video");
  const playIcon = document.getElementById("player-play-icon");
  const bigPlayBtn = document.getElementById("player-big-play-btn");
  if (!vid) return;

  if (vid.paused) {
    vid.play();
    if (playIcon) playIcon.textContent = "pause";
    if (bigPlayBtn) bigPlayBtn.style.opacity = "0";
  } else {
    vid.pause();
    if (playIcon) playIcon.textContent = "play_arrow";
    if (bigPlayBtn) bigPlayBtn.style.opacity = "1";
  }
}

function playerSkip(seconds) {
  const vid = document.getElementById("main-video");
  if (!vid) return;
  vid.currentTime = Math.max(0, Math.min(vid.duration || 0, vid.currentTime + seconds));
}

function playerSetSpeed(speed, btn) {
  const vid = document.getElementById("main-video");
  if (!vid) return;
  vid.playbackRate = speed;
  document.querySelectorAll(".speed-pill").forEach(p => {
    p.className = "px-2 py-0.5 rounded-full text-slate-300 hover:text-white speed-pill cursor-pointer";
  });
  if (btn) {
    btn.className = "px-2 py-0.5 rounded-full bg-white/20 text-white font-bold speed-pill cursor-pointer";
  }
}

function playerSetVolume(val) {
  const vid = document.getElementById("main-video");
  const volIcon = document.getElementById("player-vol-icon");
  if (!vid) return;
  vid.volume = val / 100;
  if (volIcon) {
    if (val == 0) volIcon.textContent = "volume_off";
    else if (val < 50) volIcon.textContent = "volume_down";
    else volIcon.textContent = "volume_up";
  }
}

function playerToggleMute() {
  const vid = document.getElementById("main-video");
  const slider = document.getElementById("player-volume-slider");
  if (!vid) return;
  vid.muted = !vid.muted;
  if (vid.muted) {
    if (slider) slider.value = 0;
    playerSetVolume(0);
  } else {
    if (slider) slider.value = 90;
    playerSetVolume(90);
  }
}

function playerToggleFullscreen() {
  const stage = document.getElementById("player-stage-box") || document.getElementById("main-video");
  if (!stage) return;
  if (!document.fullscreenElement) {
    stage.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
}

function playerScrubClick(e) {
  const vid = document.getElementById("main-video");
  const rail = document.getElementById("player-timeline-rail");
  if (!vid || !rail || !vid.duration) return;
  const rect = rail.getBoundingClientRect();
  const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  vid.currentTime = pos * vid.duration;
}

function copyPlayerTitle() {
  const t = document.getElementById("modal-video-title")?.textContent || "";
  navigator.clipboard.writeText(t);
  showToast("Đã sao chép tiêu đề video!", "success");
}

function copyPlayerCaption() {
  const c = document.getElementById("player-caption-snippet")?.textContent || "";
  navigator.clipboard.writeText(c.trim());
  showToast("Đã sao chép Caption xuất bản!", "success");
}

function copyPlayerVideoLink() {
  const vid = document.getElementById("main-video");
  if (!vid || !vid.src) return;
  navigator.clipboard.writeText(vid.src);
  showToast("Đã sao chép đường link Video MP4!", "success");
}

function openSeoKitFromPlayer() {
  if (!currentPlayerVideoId) return;
  closePlayerModal();
  openSeoKitModal(currentPlayerVideoId);
}

function openYouTubeFromPlayer() {
  if (!currentPlayerVideoId) return;
  closePlayerModal();
  openYouTubeUploadModal(currentPlayerVideoId);
}

function openThumbStudioFromPlayer() {
  if (!currentPlayerVideoId) return;
  closePlayerModal();
  openSeoKitModal(currentPlayerVideoId);
}
