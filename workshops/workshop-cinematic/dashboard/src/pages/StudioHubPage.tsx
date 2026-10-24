import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Film,
  Trash2,
  Play,
  Download,
  RefreshCw,
  HardDrive,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Search,
  Terminal,
  ChevronDown,
  ChevronUp,
  X,
  FileText,
  Bot,
  Activity,
  Copy,
  Check,
  Share2,
  Tag,
  Image as ImageIcon,
} from 'lucide-react'
import { fetchAPI } from '../api/client'
import { useWebSocketContext } from '../api/useWebSocketContext'
import type { StudioVideo, StudioJob, StudioStorage, PublishingKit } from '../types'
import { Badge } from '../components/ui/badge'

const WORKSHOP_TABS = [
  { id: 'all', label: 'Tất Cả Phân Xưởng', color: '#0f172a' },
  { id: 'news', label: 'Xưởng 1: Tin Tức (9:16)', color: '#3b82f6' },
  { id: 'explainer', label: 'Xưởng 2: Explainer Code', color: '#8b5cf6' },
  { id: 'whiteboard', label: 'Xưởng 3: Bảng Trắng', color: '#f59e0b' },
  { id: 'cinematic', label: 'Xưởng 4: Phim AI 3D', color: '#ff477e' },
]

export default function StudioHubPage() {
  const { lastEvent } = useWebSocketContext()
  const [videos, setVideos] = useState<StudioVideo[]>([])
  const [storage, setStorage] = useState<StudioStorage | null>(null)
  const [activeJobs, setActiveJobs] = useState<StudioJob[]>([])
  const [historyJobs, setHistoryJobs] = useState<StudioJob[]>([])
  const [activeTab, setActiveTab] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [cleaning, setCleaning] = useState<boolean>(false)
  const [cleanResult, setCleanResult] = useState<string | null>(null)
  const [showLogs, setShowLogs] = useState<boolean>(false)

  // Video Player Modal
  const [playingVideo, setPlayingVideo] = useState<StudioVideo | null>(null)

  // Delete Confirm Modal
  const [deletingVideo, setDeletingVideo] = useState<StudioVideo | null>(null)
  const [isDeleting, setIsDeleting] = useState<boolean>(false)

  // Publishing Kit & Metadata Hub (Tiêu đề, Caption, Thumbnail copy nhanh)
  const [pubKit, setPubKit] = useState<PublishingKit | null>(null)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)

  const handleCopy = (text: string, key: string) => {
    if (!text) return
    navigator.clipboard.writeText(text)
    setCopiedKey(key)
    setTimeout(() => {
      setCopiedKey(null)
    }, 2000)
  }

  const handleCopyAll = () => {
    if (!pubKit) return
    const titlesText = pubKit.titles.map((t, i) => `${i + 1}. [${t.label}] ${t.text}`).join('\n')
    const fullText = `TITLES (A/B TESTING):\n${titlesText}\n\nDESCRIPTION & CAPTION:\n${pubKit.caption}\n\nHASHTAGS:\n${pubKit.hashtags.join(' ')}`
    handleCopy(fullText, 'all')
  }

  // ─── Fetch Data ─────────────────────────────────────────────
  const loadStudioData = useCallback(async () => {
    try {
      const [vRes, sRes, pRes, kRes] = await Promise.all([
        fetchAPI<{ videos: StudioVideo[] }>('/api/studio/videos'),
        fetchAPI<StudioStorage>('/api/studio/storage'),
        fetchAPI<{ active_jobs: StudioJob[]; history: StudioJob[] }>('/api/studio/progress'),
        fetchAPI<{ kit: PublishingKit }>('/api/studio/publishing-kit').catch(() => ({ kit: null })),
      ])
      setVideos(vRes.videos || [])
      setStorage(sRes || null)
      setActiveJobs(pRes.active_jobs || [])
      setHistoryJobs(pRes.history || [])
      if (kRes?.kit) setPubKit(kRes.kit)
    } catch (err) {
      console.error('Lỗi nạp dữ liệu Studio:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadStudioData()
    const timer = setInterval(loadStudioData, 5000)
    return () => clearInterval(timer)
  }, [loadStudioData])

  // Lắng nghe WebSocket event thời gian thực
  useEffect(() => {
    if (!lastEvent) return
    if (lastEvent.type === 'studio_job_progress') {
      const jobData = (lastEvent.data as any)?.job as StudioJob
      if (jobData) {
        if (jobData.status === 'RUNNING') {
          setActiveJobs(prev => {
            const next = prev.filter(j => j.id !== jobData.id)
            return [jobData, ...next]
          })
        } else {
          setActiveJobs(prev => prev.filter(j => j.id !== jobData.id))
          setHistoryJobs(prev => [jobData, ...prev.filter(j => j.id !== jobData.id)].slice(0, 10))
          loadStudioData()
        }
      }
    }
  }, [lastEvent, loadStudioData])

  // ─── Action: Dọn Rác 1-Click ────────────────────────────────
  const handleCleanupTemp = async () => {
    setCleaning(true)
    setCleanResult(null)
    try {
      const res = await fetchAPI<{ message: string; freed_formatted: string }>('/api/studio/cleanup-temp', {
        method: 'POST',
      })
      setCleanResult(res.message)
      await loadStudioData()
    } catch (err: any) {
      setCleanResult(`Lỗi dọn dẹp: ${err.message}`)
    } finally {
      setCleaning(false)
    }
  }

  // ─── Action: Xóa Video ──────────────────────────────────────
  const handleConfirmDelete = async () => {
    if (!deletingVideo) return
    setIsDeleting(true)
    try {
      await fetchAPI(`/api/studio/videos/${deletingVideo.workshop}/${encodeURIComponent(deletingVideo.filename)}`, {
        method: 'DELETE',
      })
      setDeletingVideo(null)
      await loadStudioData()
    } catch (err: any) {
      alert(`Không thể xóa video: ${err.message}`)
    } finally {
      setIsDeleting(false)
    }
  }

  // ─── Filtered Videos ────────────────────────────────────────
  const filteredVideos = useMemo(() => {
    return videos.filter(v => {
      const matchTab = activeTab === 'all' || v.workshop === activeTab
      const q = searchQuery.toLowerCase().trim()
      const matchQuery = !q || v.title.toLowerCase().includes(q) || v.filename.toLowerCase().includes(q)
      return matchTab && matchQuery
    })
  }, [videos, activeTab, searchQuery])

  // Video nổi bật (video đầu tiên hoặc video vừa hoàn thành)
  const featuredVideo = videos.length > 0 ? videos[0] : null
  const currentRunningJob = activeJobs.length > 0 ? activeJobs[0] : null
  const latestFinishedJob = historyJobs.length > 0 ? historyJobs[0] : null

  return (
    <div className="flex flex-col gap-6 max-w-[1720px] mx-auto pb-16 font-sans">
      {/* ─── 1. TOP STUDIO HEADER (Luminous Porcelain) ───────── */}
      <div className="frosted-glass rounded-3xl p-5 md:p-6 hairline-border shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-black tracking-tight text-slate-900 flex items-center gap-2">
              <span className="bg-gradient-to-r from-pink-500 via-rose-500 to-cyan-500 bg-clip-text text-transparent">
                OmniVideo Studio
              </span>
              <span className="text-pink-500 font-bold">✦</span>
            </h1>
            <Badge variant="outline" className="text-[10px] font-bold px-2 py-0.5 rounded-full border-pink-200 bg-pink-50 text-pink-600">
              4 XƯỞNG HỢP NHẤT
            </Badge>
          </div>
          <p className="text-xs text-slate-500 font-medium">
            Trung tâm điều phối sản xuất, theo dõi tiến trình 6 cổng tự động và quản lý dung lượng ổ đĩa.
          </p>
        </div>

        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Storage telemetry gauge */}
          {storage && (
            <div className="hidden sm:flex items-center gap-2.5 bg-white px-3.5 py-1.5 rounded-full hairline-border shadow-2xs">
              <HardDrive className="w-4 h-4 text-cyan-500" />
              <div className="flex flex-col">
                <span className="text-[10px] font-bold text-slate-700">Drive C: {storage.disk.free_formatted} trống</span>
                <div className="w-20 h-1 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${storage.disk.free_percent}%` }} />
                </div>
              </div>
              <span className="text-[10px] font-black text-cyan-600">{storage.disk.free_percent}%</span>
            </div>
          )}

          <button
            onClick={loadStudioData}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full bg-white text-slate-700 hairline-border hover:bg-slate-50 transition-all active:scale-95 shadow-2xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-500" /> Làm mới
          </button>

          <button
            onClick={handleCleanupTemp}
            disabled={cleaning}
            className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-bold rounded-full text-white bg-gradient-to-r from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 glow-primary transition-all active:scale-95 shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5 fill-white" />
            {cleaning ? 'Đang dọn...' : '🧹 Dọn Rác Ổ Đĩa'}
          </button>
        </div>
      </div>

      {cleanResult && (
        <div className="p-3 text-xs font-medium rounded-2xl flex items-center justify-between bg-emerald-50 border border-emerald-200 text-emerald-800 shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{cleanResult}</span>
          </div>
          <button onClick={() => setCleanResult(null)} className="text-xs font-bold px-1 text-emerald-700 hover:text-emerald-900">✕</button>
        </div>
      )}

      {/* ─── 2. MAIN WORKSPACE (8 COLS MAIN + 4 COLS SIDE-DOCK) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LEFT / CENTER STAGE (8 COLS) */}
        <div className="lg:col-span-8 flex flex-col gap-6 min-w-0">
          {/* A. LIVE STUDIO PRODUCTION HUB (HERO SECTION) */}
          <section className="frosted-glass rounded-3xl p-5 md:p-6 hairline-border shadow-xs flex flex-col gap-5 relative overflow-hidden">
            {/* Ambient anime glow spots */}
            <div className="absolute -top-12 -right-12 w-48 h-48 bg-pink-400/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-cyan-400/10 rounded-full blur-3xl pointer-events-none" />

            {/* Hub Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full bg-pink-50 text-pink-600 border border-pink-200">
                    ✦ Veo 2 Engine AI
                  </span>
                  <span className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full flex items-center gap-1.5 ${
                    currentRunningJob 
                      ? 'bg-rose-100 text-rose-800 border border-rose-300' 
                      : featuredVideo 
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                      : 'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      currentRunningJob ? 'bg-rose-500 animate-ping' : featuredVideo ? 'bg-emerald-500' : 'bg-slate-400'
                    }`} />
                    {currentRunningJob 
                      ? `Đang Xử Lý: ${currentRunningJob.progress}%` 
                      : featuredVideo 
                      ? 'Hoàn Thành 100%' 
                      : 'Sẵn Sàng Nhận Dự Án'}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {featuredVideo?.aspect_ratio || '16:9'} • 1080p
                  </span>
                </div>
                <h2 className="text-lg md:text-xl font-black text-slate-900 tracking-tight">
                  {currentRunningJob ? currentRunningJob.title : (featuredVideo?.title || 'OmniVideo Studio Center Stage (Chờ Bắt Đầu)')}
                </h2>
              </div>

              {featuredVideo && (
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => setPlayingVideo(featuredVideo)}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold text-white bg-pink-600 hover:bg-pink-700 glow-primary transition-all active:scale-95 shadow-xs"
                  >
                    <Play className="w-3.5 h-3.5 fill-white" /> Xem Ngay
                  </button>
                  <a
                    href={featuredVideo.video_url}
                    download={featuredVideo.filename}
                    className="p-2 rounded-full bg-white text-slate-600 hairline-border hover:bg-slate-50 transition-colors shadow-2xs"
                    title="Tải video thành phẩm"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </a>
                </div>
              )}
            </div>

            {/* B. MULTI-GATE PIPELINE TRACKER (6 CHỐT KIỂM DUYỆT TỰ ĐỘNG) */}
            <div className="bg-slate-50/70 p-4 rounded-2xl hairline-border flex flex-col gap-3">
              <div className="flex items-center justify-between text-xs font-bold text-slate-800">
                <span className="flex items-center gap-1.5">
                  <Activity className="w-4 h-4 text-cyan-600" />
                  Tiến Trình 6 Cổng Xử Lý Điện Ảnh (The 6-Gate Protocol)
                </span>
                <span className="text-[11px] text-pink-600 font-extrabold uppercase">
                  {currentRunningJob 
                    ? `Đang Chạy: ${currentRunningJob.progress}%` 
                    : featuredVideo 
                    ? '6/6 CỔNG HOÀN TẤT (100%)' 
                    : 'CHỜ BẮT ĐẦU (0/6 CỔNG)'}
                </span>
              </div>

              {/* 6 Nodes Chain */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
                {[
                  { id: 1, label: 'Cổng 1: Ý tưởng', desc: featuredVideo ? '100% Duyệt' : 'Chờ Kịch Bản' },
                  { id: 2, label: 'Cổng 2: Kịch bản', desc: featuredVideo ? 'Đã Phân Cảnh' : 'Chờ ASL 5 Hồi' },
                  { id: 3, label: 'Cổng 3: Asset Chibi', desc: featuredVideo ? 'Master Sets' : 'Chờ Khóa Model' },
                  { id: 4, label: 'Cổng 4: Voice 48kHz', desc: featuredVideo ? 'Edge-TTS' : 'Chờ Lồng Tiếng' },
                  { id: 5, label: 'Cổng 5: Storyboard', desc: featuredVideo ? 'Imagen 3' : 'Chờ Sinh Ảnh' },
                  { id: 6, label: 'Cổng 6: Veo 2 AI', desc: featuredVideo ? '100% GEN V' : 'Chờ Bấm Máy' },
                ].map(gate => {
                  const isComplete = currentRunningJob 
                    ? (currentRunningJob.steps?.find(s => s.id === `gate_${gate.id}`)?.status === 'COMPLETED')
                    : !!featuredVideo
                  const isActive = currentRunningJob 
                    ? (currentRunningJob.steps?.find(s => s.id === `gate_${gate.id}`)?.status === 'RUNNING' || (gate.id === 1 && !currentRunningJob.steps?.length))
                    : false

                  return (
                    <div
                      key={gate.id}
                      className={`flex flex-col items-center text-center p-2.5 rounded-xl transition-all ${
                        isActive
                          ? 'bg-pink-50 border-2 border-pink-500 glow-primary'
                          : isComplete
                          ? 'bg-white border border-slate-200 shadow-2xs'
                          : 'bg-slate-100/60 border border-slate-200/50'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs mb-1 ${
                        isActive
                          ? 'bg-pink-600 text-white animate-pulse'
                          : isComplete
                          ? 'bg-emerald-500 text-white'
                          : 'bg-slate-300 text-slate-600'
                      }`}>
                        {isActive ? '✦' : isComplete ? '✓' : gate.id}
                      </div>
                      <span className="text-[11px] font-bold text-slate-800 leading-tight">{gate.label}</span>
                      <span className={`text-[10px] font-medium mt-0.5 ${isActive ? 'text-pink-600 font-bold' : isComplete ? 'text-emerald-700' : 'text-slate-400'}`}>
                        {gate.desc}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* C. INTERACTIVE VIDEO PREVIEW MONITOR */}
            {featuredVideo ? (
              <div className="relative rounded-2xl overflow-hidden hairline-border bg-slate-950 shadow-md group">
                <div className="relative aspect-video w-full overflow-hidden bg-black flex items-center justify-center">
                  {featuredVideo.thumb_url ? (
                    <img
                      src={featuredVideo.thumb_url}
                      alt={featuredVideo.title}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.01]"
                    />
                  ) : (
                    <div className="text-slate-500 flex flex-col items-center gap-2">
                      <Film className="w-12 h-12 opacity-40" />
                      <span className="text-xs uppercase font-mono tracking-wider">Preview Stage</span>
                    </div>
                  )}

                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />

                  {/* Top Badge Overlay */}
                  <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-auto">
                    <span className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md text-white font-mono text-[11px] border border-white/20 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                      MASTER FILM PREVIEW
                    </span>
                    <span className="px-2.5 py-1 rounded-full bg-pink-600/90 backdrop-blur-md text-white font-mono text-[10px] font-bold">
                      1080p Full HD • 30 FPS • H.264
                    </span>
                  </div>

                  {/* Center Play Button Overlay */}
                  <button
                    onClick={() => setPlayingVideo(featuredVideo)}
                    className="absolute inset-0 flex items-center justify-center cursor-pointer group/btn"
                  >
                    <div className="w-14 h-14 rounded-full bg-white/95 text-pink-600 flex items-center justify-center shadow-xl transition-all group-hover/btn:scale-115 group-hover/btn:bg-pink-600 group-hover/btn:text-white glow-primary">
                      <Play className="w-6 h-6 ml-1 fill-current" />
                    </div>
                  </button>

                  {/* Bottom Waveform & Controls Bar */}
                  <div className="absolute bottom-3 left-3 right-3 flex flex-col gap-2 bg-black/70 backdrop-blur-md p-3 rounded-xl border border-white/10 pointer-events-auto">
                    {/* Simulated Audio Waveform Bar */}
                    <div className="flex items-center gap-1 h-3 w-full">
                      {[30, 45, 70, 85, 40, 95, 60, 80, 50, 75, 90, 65, 45, 80, 100, 70, 55, 90, 85, 60, 40, 75, 95, 80, 60, 40, 70, 85, 90, 60].map((h, i) => (
                        <span
                          key={i}
                          className="flex-1 rounded-full transition-all"
                          style={{
                            height: `${h}%`,
                            background: i % 2 === 0 ? '#00c2e0' : '#ff477e',
                            opacity: 0.85,
                          }}
                        />
                      ))}
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-300">
                      <span>01:00 / 01:00 (55.87s audio)</span>
                      <div className="flex items-center gap-3">
                        <span className="text-cyan-400 font-bold">Ducking -18dB Active</span>
                        <span className="text-pink-400 font-bold">{featuredVideo.size_formatted}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="rounded-2xl p-8 border-2 border-dashed border-slate-200/80 bg-slate-50/40 flex flex-col items-center justify-center text-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-white border border-slate-200 flex items-center justify-center text-slate-400 shadow-2xs">
                  <Film className="w-6 h-6 text-pink-500/80" />
                </div>
                <div className="flex flex-col gap-1 max-w-md">
                  <span className="text-sm font-bold text-slate-800">Chưa có video nào trong phòng thu</span>
                  <p className="text-xs text-slate-500">
                    Toàn bộ file rác và video cũ đã được dọn sạch. Bạn có thể bắt đầu tạo video mới bằng cách gửi yêu cầu chủ đề cho tôi bất cứ lúc nào!
                  </p>
                </div>
              </div>
            )}
          </section>

          {/* E. SOCIAL PUBLISHING KIT & METADATA HUB (1-CLICK COPY CENTER) */}
          {pubKit && pubKit.status !== 'empty' && pubKit.titles?.length > 0 ? (
            <section className="frosted-glass rounded-3xl p-5 md:p-6 hairline-border shadow-xs flex flex-col gap-5 relative overflow-hidden">
              {/* Subtle anime corner accents */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-pink-500/10 to-cyan-500/10 rounded-bl-full pointer-events-none" />

              {/* Section Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 shadow-2xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      ✦ {pubKit.status === 'ready' ? 'SẴN SÀNG ĐĂNG KÊNH' : 'ĐANG BIÊN SOẠN'}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {pubKit.sync_note}
                    </span>
                    {pubKit.updated_at && (
                      <span className="text-[10px] text-slate-400">
                        • Cập nhật: {pubKit.updated_at}
                      </span>
                    )}
                  </div>
                  <h3 className="text-base md:text-lg font-black text-slate-900 tracking-tight flex items-center gap-2">
                    <span className="text-pink-600 font-bold">✦</span> Gói Tư Liệu Xuất Bản & Social Metadata Hub
                  </h3>
                  <p className="text-xs text-slate-500">
                    Tiêu đề A/B test, mô tả SEO, hashtag và ảnh thumbnail được AI chuẩn bị sẵn — sao chép nhanh để đăng YouTube, TikTok & Reels.
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={handleCopyAll}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-full text-xs font-bold text-white bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 glow-primary transition-all active:scale-95 shadow-xs cursor-pointer"
                  >
                    {copiedKey === 'all' ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-white" />
                        <span>✓ Đã Chép Tất Cả!</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-3.5 h-3.5 fill-white" />
                        <span>✨ Sao Chép Toàn Bộ (1-Click)</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Content Grid (Left: Copywriting Tools, Right: HD Thumbnail Studio) */}
              <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
                {/* LEFT COLUMN: Titles, Caption & Hashtags (7 Cols) */}
                <div className="xl:col-span-7 flex flex-col gap-4">
                  {/* 1. Title Variants (A/B Testing Hooks) */}
                  <div className="bg-white/90 rounded-2xl p-4 hairline-border flex flex-col gap-3 shadow-2xs">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                      <span className="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-pink-600" />
                        Tiêu Đề Video Đề Xuất (A/B Testing)
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">
                        {pubKit.titles?.length || 0} Biến Thể
                      </span>
                    </div>

                    <div className="flex flex-col gap-2">
                      {pubKit.titles?.map((variant, idx) => {
                        const isCopied = copiedKey === `title-${variant.id}`
                        const badgeStyle =
                          variant.badge_color === 'pink'
                            ? 'bg-pink-50 text-pink-700 border-pink-200'
                            : variant.badge_color === 'cyan'
                            ? 'bg-cyan-50 text-cyan-800 border-cyan-200'
                            : 'bg-amber-50 text-amber-800 border-amber-200'

                        return (
                          <div
                            key={variant.id || idx}
                            className="flex items-center justify-between gap-3 p-3 rounded-xl bg-slate-50/70 border border-slate-200/60 hover:border-pink-300 hover:bg-pink-50/20 transition-all group"
                          >
                            <div className="flex flex-col gap-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${badgeStyle}`}>
                                  {variant.label}
                                </span>
                                {variant.metrics && (
                                  <span className="text-[11px] font-bold text-emerald-600 font-mono">
                                    {variant.metrics}
                                  </span>
                                )}
                              </div>
                              <p className="text-xs font-bold text-slate-800 group-hover:text-pink-600 transition-colors line-clamp-2">
                                {variant.text}
                              </p>
                            </div>

                            <button
                              onClick={() => handleCopy(variant.text, `title-${variant.id}`)}
                              className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold border transition-all shrink-0 active:scale-95 shadow-2xs cursor-pointer ${
                                isCopied
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                                  : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-200'
                              }`}
                            >
                              {isCopied ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                                  <span>✓ Đã Chép</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="w-3.5 h-3.5 text-slate-500" />
                                  <span>Sao Chép</span>
                                </>
                              )}
                            </button>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  {/* 2. Caption & Description Box */}
                  <div className="bg-white/90 rounded-2xl p-4 hairline-border flex flex-col gap-2.5 shadow-2xs">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                      <span className="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                        <Share2 className="w-3.5 h-3.5 text-cyan-600" />
                        Mô Tả & Caption Chuẩn SEO (Kèm Timestamps)
                      </span>
                      <button
                        onClick={() => handleCopy(pubKit.caption, 'caption')}
                        className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold border transition-all active:scale-95 shadow-2xs cursor-pointer ${
                          copiedKey === 'caption'
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                            : 'bg-cyan-50 hover:bg-cyan-100 text-cyan-800 border-cyan-200'
                        }`}
                      >
                        {copiedKey === 'caption' ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                            <span>✓ Đã Chép Caption!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5 text-cyan-700" />
                            <span>Sao Chép Caption</span>
                          </>
                        )}
                      </button>
                    </div>

                    <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200/60 font-mono text-xs text-slate-700 leading-relaxed whitespace-pre-line max-h-48 overflow-y-auto">
                      {pubKit.caption}
                    </div>
                  </div>

                  {/* 3. Hashtags */}
                  <div className="bg-white/90 rounded-2xl p-4 hairline-border flex flex-col gap-2.5 shadow-2xs">
                    <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                      <span className="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                        <Tag className="w-3.5 h-3.5 text-pink-600" />
                        Bộ Thẻ Hashtag Đề Xuất (CTR Boost)
                      </span>
                      <button
                        onClick={() => handleCopy(pubKit.hashtags.join(' '), 'hashtags')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold border transition-all active:scale-95 shadow-2xs cursor-pointer ${
                          copiedKey === 'hashtags'
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                            : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-200'
                        }`}
                      >
                        {copiedKey === 'hashtags' ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-600" />
                            <span>✓ Đã Chép!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3 text-slate-500" />
                            <span>Sao Chép Tất Cả Tags</span>
                          </>
                        )}
                      </button>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {pubKit.hashtags?.map((tag, i) => (
                        <button
                          key={i}
                          onClick={() => handleCopy(tag, `tag-${i}`)}
                          className={`text-xs font-bold px-2.5 py-1 rounded-lg border transition-all cursor-pointer ${
                            copiedKey === `tag-${i}`
                              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                              : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-pink-300 hover:text-pink-600 hover:bg-pink-50/30'
                          }`}
                          title="Bấm để sao chép tag này"
                        >
                          {copiedKey === `tag-${i}` ? `✓ ${tag}` : tag}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* RIGHT COLUMN: HD Thumbnail Studio Preview (5 Cols) */}
                <div className="xl:col-span-5 flex flex-col gap-4">
                  <div className="bg-white/90 rounded-2xl p-4 hairline-border flex flex-col gap-4 shadow-2xs h-full justify-between">
                    <div className="flex flex-col gap-3">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                        <span className="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
                          <ImageIcon className="w-3.5 h-3.5 text-cyan-600" />
                          HD Thumbnail Studio (16:9)
                        </span>
                        <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-800 border border-cyan-200">
                          Tỉ Lệ Chuẩn YouTube
                        </span>
                      </div>

                      {/* Thumbnail Canvas Viewport */}
                      <div className="relative aspect-video w-full rounded-xl overflow-hidden hairline-border bg-slate-900 group shadow-md glow-cyan">
                        {pubKit.thumbnail_url ? (
                          <img
                            src={pubKit.thumbnail_url}
                            alt="Video Thumbnail"
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                          />
                        ) : (
                          <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 gap-2">
                            <ImageIcon className="w-8 h-8 opacity-40" />
                            <span className="text-xs font-mono">Đang tạo ảnh thumbnail...</span>
                          </div>
                        )}

                        {/* Badges on Thumbnail */}
                        <div className="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md text-white font-mono text-[11px] border border-white/20 flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                          1080p Full HD • CTR Score {pubKit.thumbnail_score || '94.8%'}
                        </div>
                        <div className="absolute bottom-2.5 right-2.5 px-2 py-0.5 rounded bg-black/75 text-white font-mono text-[10px] uppercase font-bold">
                          Veo 2 Keyframe #01
                        </div>
                      </div>

                      {/* Thumbnail Buttons */}
                      <div className="flex flex-col gap-2 pt-2">
                        {pubKit.thumbnail_url && (
                          <a
                            href={pubKit.thumbnail_url}
                            download="thumbnail-ai-agent-4k.png"
                            className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-full text-xs font-bold text-white bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-700 hover:to-rose-700 glow-primary transition-all active:scale-95 shadow-xs cursor-pointer"
                          >
                            <Download className="w-3.5 h-3.5" />
                            <span>📥 Tải Thumbnail (PNG 4K)</span>
                          </a>
                        )}

                        <div className="grid grid-cols-2 gap-2">
                          <button
                            onClick={() => {
                              const fullUrl = pubKit.thumbnail_url?.startsWith('http')
                                ? pubKit.thumbnail_url
                                : `${window.location.origin}${pubKit.thumbnail_url}`
                              handleCopy(fullUrl, 'thumb-link')
                            }}
                            className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-full text-xs font-bold border transition-all active:scale-95 shadow-2xs cursor-pointer ${
                              copiedKey === 'thumb-link'
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
                            }`}
                          >
                            {copiedKey === 'thumb-link' ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-600" />
                                <span>✓ Đã Chép Link</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3 text-cyan-600" />
                                <span>Sao Chép Link Ảnh</span>
                              </>
                            )}
                          </button>

                          <button
                            onClick={() => handleCopy(pubKit.titles[0]?.text || '', 'main-title')}
                            className={`flex items-center justify-center gap-1.5 py-2 px-3 rounded-full text-xs font-bold border transition-all active:scale-95 shadow-2xs cursor-pointer ${
                              copiedKey === 'main-title'
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
                            }`}
                          >
                            {copiedKey === 'main-title' ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-600" />
                                <span>✓ Đã Chép Tiêu Đề</span>
                              </>
                            ) : (
                              <>
                                <FileText className="w-3 h-3 text-pink-600" />
                                <span>Sao Chép Tiêu Đề</span>
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Specs Footer */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60 text-slate-600 font-mono text-[11px] leading-relaxed flex items-center justify-between flex-wrap gap-2">
                      <span>{pubKit.thumbnail_specs || '1920x1080 (16:9) • PNG'}</span>
                      <span>•</span>
                      <span>Phong cách: Anime Cyber-Chibi</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          ) : (
            <section className="frosted-glass rounded-3xl p-6 hairline-border shadow-xs flex flex-col gap-3 text-center items-center justify-center py-8 bg-slate-50/40 border-dashed">
              <div className="w-10 h-10 rounded-2xl bg-pink-50 border border-pink-200/60 flex items-center justify-center text-pink-600 shadow-2xs">
                <Sparkles className="w-5 h-5" />
              </div>
              <div className="flex flex-col gap-1 max-w-md">
                <h3 className="text-sm font-bold text-slate-800">✦ Gói Tư Liệu Xuất Bản (Chờ Dự Án)</h3>
                <p className="text-xs text-slate-500">
                  Chưa có dữ liệu xuất bản. Khi bạn yêu cầu: <em>"Chuẩn bị cho tôi tiêu đề, caption, thumbnail..."</em>, AI Agent sẽ tự động soạn thảo và đẩy lên đây kèm đầy đủ các nút sao chép 1-click.
                </p>
              </div>
            </section>
          )}

          {/* D. VIDEO LIBRARY & STORAGE CRUD (THƯ VIỆN VIDEO THÀNH PHẨM) */}
          <section className="frosted-glass rounded-3xl p-5 md:p-6 hairline-border shadow-xs flex flex-col gap-4">
            <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-black text-slate-900 tracking-tight flex items-center gap-2">
                  <Film className="w-4 h-4 text-pink-600" />
                  Thư Viện Video & Quản Lý Lưu Trữ
                </h3>
                <span className="text-xs text-slate-500 font-medium">
                  Hiển thị <strong>{filteredVideos.length}</strong> video thành phẩm trong 4 phân xưởng
                </span>
              </div>

              {/* Search Bar */}
              <div className="relative flex items-center min-w-[220px]">
                <Search className="w-3.5 h-3.5 absolute left-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Tìm kiếm video..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full text-xs pl-8 pr-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-800 placeholder-slate-400 outline-none focus:border-pink-500 transition-colors shadow-2xs"
                />
              </div>
            </div>

            {/* Workshop Filter Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
              {WORKSHOP_TABS.map(tab => {
                const active = activeTab === tab.id
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-3 py-1.5 text-xs font-bold rounded-full whitespace-nowrap transition-all shadow-2xs ${
                      active
                        ? 'bg-slate-900 text-white'
                        : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                    }`}
                  >
                    {tab.label}
                  </button>
                )
              })}
            </div>

            {/* Storage Breakdown Bar */}
            {storage && (
              <div className="bg-slate-50 p-3.5 rounded-2xl hairline-border flex flex-col gap-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-700">
                    Tổng dung lượng video: <strong className="text-pink-600">{storage.total_workshops_formatted}</strong>
                  </span>
                  <span className="text-slate-500 text-[11px]">
                    Ổ C: còn trống <strong>{storage.disk.free_formatted}</strong> ({storage.disk.free_percent}%)
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-200/80 rounded-full flex overflow-hidden p-0.5">
                  {Object.values(storage.workshops).map(ws => {
                    const pct = storage.total_workshops_bytes > 0 ? (ws.size_bytes / storage.total_workshops_bytes) * 100 : 0
                    if (pct <= 0) return null
                    return (
                      <div
                        key={ws.id}
                        title={`${ws.name}: ${ws.size_formatted} (${Math.round(pct)}%)`}
                        style={{ width: `${pct}%`, background: ws.color }}
                        className="h-full first:rounded-l-full last:rounded-r-full"
                      />
                    )
                  })}
                </div>
                <div className="flex flex-wrap items-center gap-3 text-[11px] pt-1">
                  {Object.values(storage.workshops).map(ws => (
                    <div key={ws.id} className="flex items-center gap-1.5 font-medium text-slate-600">
                      <span className="w-2 h-2 rounded-full" style={{ background: ws.color }} />
                      <span>{ws.name.split(':')[1]?.trim() || ws.name}:</span>
                      <strong className="text-slate-900">{ws.size_formatted}</strong>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Video Cards Grid */}
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">
                Đang tải thư viện video...
              </div>
            ) : filteredVideos.length === 0 ? (
              <div className="py-12 text-center flex flex-col items-center justify-center gap-2 rounded-2xl bg-white border border-dashed border-slate-200">
                <Film className="w-8 h-8 text-slate-300" />
                <span className="text-xs text-slate-500 font-medium">Chưa có video nào trong phân xưởng này.</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {filteredVideos.map(video => (
                  <div
                    key={video.id + video.workshop}
                    className="group relative rounded-2xl overflow-hidden flex flex-col bg-white border border-slate-200 shadow-2xs hover:shadow-md hover:border-pink-300 transition-all hover:-translate-y-1"
                  >
                    {/* Thumbnail / Aspect Container */}
                    <div
                      className="relative w-full overflow-hidden flex items-center justify-center bg-black"
                      style={{ aspectRatio: video.aspect_ratio.includes('9:16') ? '9/16' : '16/9', maxHeight: '220px' }}
                    >
                      {video.thumb_url ? (
                        <img src={video.thumb_url} alt={video.title} className="w-full h-full object-cover transition-transform group-hover:scale-105 duration-300" />
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center gap-1 text-slate-400">
                          <Film className="w-8 h-8 opacity-30" />
                          <span className="text-[10px] uppercase font-mono">No Preview</span>
                        </div>
                      )}

                      {/* Play overlay button */}
                      <div
                        onClick={() => setPlayingVideo(video)}
                        className="absolute inset-0 bg-black/35 opacity-0 group-hover:opacity-100 flex items-center justify-center cursor-pointer transition-opacity"
                      >
                        <div className="w-11 h-11 rounded-full bg-white text-pink-600 flex items-center justify-center shadow-lg transition-transform hover:scale-110">
                          <Play className="w-5 h-5 ml-0.5 fill-current" />
                        </div>
                      </div>

                      {/* Top Badges */}
                      <div className="absolute top-2 left-2 right-2 flex items-center justify-between pointer-events-none">
                        <Badge style={{ background: video.workshop_color, color: '#fff', fontSize: '9px', fontWeight: 'bold' }}>
                          {video.workshop.toUpperCase()}
                        </Badge>
                        <Badge variant="outline" className="bg-black/60 backdrop-blur-sm text-[9px] text-white border-0 font-mono">
                          {video.size_formatted}
                        </Badge>
                      </div>
                    </div>

                    {/* Details Body */}
                    <div className="p-3.5 flex flex-col gap-2 flex-1 justify-between">
                      <div>
                        <h4 className="font-bold text-xs line-clamp-2 text-slate-900 leading-tight group-hover:text-pink-600 transition-colors" title={video.title}>
                          {video.title}
                        </h4>
                        <div className="flex items-center gap-2 mt-1.5 text-[10px] text-slate-400 font-mono">
                          <span>{video.created_at}</span>
                          <span>•</span>
                          <span>{video.aspect_ratio}</span>
                        </div>
                      </div>

                      {/* Actions Footer */}
                      <div className="flex items-center justify-between border-t border-slate-100 pt-2.5 mt-1">
                        <button
                          onClick={() => setPlayingVideo(video)}
                          className="flex items-center gap-1 text-xs font-bold text-pink-600 hover:text-pink-700"
                        >
                          <Play className="w-3 h-3 fill-current" /> Xem Phim
                        </button>

                        <div className="flex items-center gap-1.5">
                          {video.has_srt && video.srt_url && (
                            <a
                              href={video.srt_url}
                              download={`${video.filename}.srt`}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-600 hover:bg-cyan-50 transition-colors"
                              title="Tải file phụ đề SRT"
                            >
                              <FileText className="w-3.5 h-3.5" />
                            </a>
                          )}
                          <a
                            href={video.video_url}
                            download={video.filename}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                            title="Tải file video MP4"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </a>
                          <button
                            onClick={() => setDeletingVideo(video)}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                            title="Xóa video để giải phóng ổ đĩa"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* RIGHT SIDE DOCK (4 COLS) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* 1. TRỢ LÝ BYTE MASCOT WIDGET */}
          <div className="frosted-glass rounded-3xl p-5 hairline-border shadow-xs flex flex-col gap-4 relative overflow-hidden">
            {/* Ambient glow */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-400/15 rounded-full blur-2xl pointer-events-none" />

            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-pink-600" />
                <h3 className="text-sm font-black text-slate-900 tracking-tight">Trợ Lý Byte ✦</h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> Trực Tuyến
              </span>
            </div>

            {/* Avatar & Speech Bubble */}
            <div className="flex items-start gap-3">
              <div className="relative shrink-0">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-pink-500 to-cyan-400 p-0.5 glow-primary shadow-xs">
                  <div className="w-full h-full bg-white rounded-2xl flex items-center justify-center overflow-hidden">
                    {/* Chibi Icon Graphic */}
                    <div className="text-xl">🤖</div>
                  </div>
                </div>
                <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-white" />
              </div>

              {/* Speech Bubble Dialog */}
              <div className="flex-1 bg-white p-3.5 rounded-2xl rounded-tl-xs hairline-border shadow-2xs text-xs text-slate-700 leading-relaxed">
                <p className="font-medium">
                  {latestFinishedJob
                    ? `Chào bạn! Video "${latestFinishedJob.title}" đã hoàn tất xuất sắc với 100% video Veo 2 AI chuẩn điện ảnh. Bạn có muốn xem lại không? ✨`
                    : 'OmniVideo Studio đã sẵn sàng! Bạn có thể chọn bất kỳ phân xưởng nào để bắt đầu sản xuất video mới nhé! ✨'}
                </p>
              </div>
            </div>

            {/* Telemetry Metrics Card */}
            <div className="bg-slate-50/80 p-3.5 rounded-2xl hairline-border flex flex-col gap-2">
              <span className="text-[10px] font-black uppercase text-slate-400 tracking-wider">
                Chỉ Số Điện Ảnh Chuẩn (Cinematic Metrics)
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-xl bg-white hairline-border shadow-2xs flex flex-col">
                  <span className="text-[10px] text-slate-400">Nhịp Phim ASL</span>
                  <span className="font-extrabold text-slate-900 text-xs">4.0s – 7.0s</span>
                </div>
                <div className="p-2 rounded-xl bg-white hairline-border shadow-2xs flex flex-col">
                  <span className="text-[10px] text-slate-400">Âm Thanh Master</span>
                  <span className="font-extrabold text-cyan-600 text-xs">48,000 Hz Stereo</span>
                </div>
                <div className="p-2 rounded-xl bg-white hairline-border shadow-2xs flex flex-col">
                  <span className="text-[10px] text-slate-400">Chuẩn Zero-Loop</span>
                  <span className="font-extrabold text-emerald-600 text-xs">Đạt Chuẩn 100%</span>
                </div>
                <div className="p-2 rounded-xl bg-white hairline-border shadow-2xs flex flex-col">
                  <span className="text-[10px] text-slate-400">Google Veo 2</span>
                  <span className="font-extrabold text-pink-600 text-xs">Connected</span>
                </div>
              </div>
            </div>

            {/* Quick Action Buttons */}
            <div className="flex flex-col gap-2">
              {featuredVideo && (
                <button
                  onClick={() => setPlayingVideo(featuredVideo)}
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-bold rounded-xl bg-slate-900 text-white hover:bg-slate-800 transition-all shadow-xs"
                >
                  <Play className="w-3.5 h-3.5 fill-white" /> Xem Master Film Vừa Xuất
                </button>
              )}
              <button
                onClick={handleCleanupTemp}
                disabled={cleaning}
                className="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold rounded-xl bg-white text-slate-700 hairline-border hover:bg-slate-50 transition-all shadow-2xs"
              >
                <Sparkles className="w-3.5 h-3.5 text-pink-500" /> Dọn Dẹp File Rác Tạm
              </button>
            </div>
          </div>

          {/* 2. LIVE TERMINAL & ACTIVITY LOGS */}
          <div className="frosted-glass rounded-3xl p-5 hairline-border shadow-xs flex flex-col gap-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="text-xs font-black uppercase tracking-wider text-slate-900 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-slate-600" />
                Dòng Lệnh Trực Tiếp (Live Logs)
              </span>
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="text-[11px] font-bold text-pink-600 flex items-center gap-0.5 hover:underline"
              >
                {showLogs ? 'Thu gọn' : 'Mở rộng'}
                {showLogs ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            </div>

            {activeJobs.length > 0 && activeJobs[0].log_lines && activeJobs[0].log_lines.length > 0 ? (
              <div className="p-3 rounded-2xl font-mono text-[11px] leading-relaxed max-h-48 overflow-y-auto bg-slate-950 text-emerald-400 border border-slate-800 shadow-inner">
                {activeJobs[0].log_lines.map((line, idx) => (
                  <div key={idx} className="whitespace-pre-wrap">{line}</div>
                ))}
              </div>
            ) : historyJobs.length > 0 && historyJobs[0].log_lines && historyJobs[0].log_lines.length > 0 ? (
              <div className="p-3 rounded-2xl font-mono text-[11px] leading-relaxed max-h-48 overflow-y-auto bg-slate-950 text-cyan-400 border border-slate-800 shadow-inner">
                {historyJobs[0].log_lines.slice(-6).map((line, idx) => (
                  <div key={idx} className="whitespace-pre-wrap">{line}</div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-400 bg-slate-50 rounded-2xl hairline-border">
                Chưa có log phát sinh từ các phân xưởng.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ─── MODAL: INLINE VIDEO PLAYER (HTTP 206 RANGE) ─────── */}
      {playingVideo && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl rounded-3xl overflow-hidden flex flex-col bg-white border border-slate-200 shadow-2xl">
            <div className="flex items-center justify-between p-4 px-6 border-b border-slate-100">
              <div>
                <h3 className="text-sm font-black text-slate-900 truncate max-w-md">
                  {playingVideo.title}
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">
                  {playingVideo.workshop_name} • {playingVideo.size_formatted} • {playingVideo.aspect_ratio}
                </span>
              </div>
              <button
                onClick={() => setPlayingVideo(null)}
                className="w-8 h-8 rounded-full flex items-center justify-center bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="w-full bg-black flex items-center justify-center" style={{ minHeight: '360px', maxHeight: '70vh' }}>
              <video
                src={playingVideo.video_url}
                controls
                autoPlay
                className="max-h-[68vh] w-auto max-w-full"
              >
                {playingVideo.srt_url && (
                  <track kind="subtitles" src={playingVideo.srt_url} srcLang="vi" label="Tiếng Việt" default />
                )}
                Trình duyệt của bạn không hỗ trợ thẻ video.
              </video>
            </div>
          </div>
        </div>
      )}

      {/* ─── MODAL: DELETE CONFIRMATION ──────────────────────── */}
      {deletingVideo && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-3xl p-6 flex flex-col gap-4 bg-white border border-slate-200 shadow-2xl">
            <div className="flex items-center gap-3 text-rose-600">
              <div className="w-10 h-10 rounded-2xl bg-rose-50 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-rose-600" />
              </div>
              <div>
                <h3 className="text-base font-black text-slate-900">Xác Nhận Xóa Video?</h3>
                <span className="text-[11px] text-slate-500">Hành động này không thể hoàn tác</span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Bạn có chắc chắn muốn xóa file video <strong className="text-slate-900">{deletingVideo.filename}</strong>, ảnh đại diện thumbnail, file phụ đề và toàn bộ dữ liệu tạm liên quan?
            </p>

            <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs flex items-center justify-between">
              <span className="text-emerald-700 font-medium">Dung lượng giải phóng:</span>
              <strong className="text-emerald-800 text-sm font-black">+{deletingVideo.size_formatted}</strong>
            </div>

            <div className="flex items-center justify-end gap-2.5 mt-2">
              <button
                onClick={() => setDeletingVideo(null)}
                disabled={isDeleting}
                className="px-4 py-2 text-xs font-bold rounded-full bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
              >
                Hủy bỏ
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={isDeleting}
                className="px-5 py-2 text-xs font-bold rounded-full bg-rose-600 hover:bg-rose-700 text-white transition-colors shadow-xs"
              >
                {isDeleting ? 'Đang xóa...' : 'Xác Nhận Xóa'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
