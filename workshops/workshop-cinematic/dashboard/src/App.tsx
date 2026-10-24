import { useState, useEffect } from 'react'
import { BrowserRouter, NavLink, Routes, Route, useLocation, useParams, useSearchParams } from 'react-router-dom'
import { LayoutDashboard, FolderOpen, Film, ScrollText, BookOpen, SlidersHorizontal, Clapperboard, Sparkles } from 'lucide-react'
import { TooltipProvider } from '@/components/ui/tooltip'
import { WebSocketProvider } from './api/WebSocketContext'
import { useWebSocketContext } from './api/useWebSocketContext'
import { LanguageProvider } from './i18n/LanguageContext'
import { useTranslation } from './i18n/useTranslation'
import { LANGS, LANG_LABELS, type Lang } from './i18n/translations'
import type { TranslationKey } from './i18n/translations'
import { fetchAPI } from './api/client'
import type { Project } from './types'
import StudioHubPage from './pages/StudioHubPage'
import DashboardPage from './pages/DashboardPage'
import ProjectsPage from './pages/ProjectsPage'
import LogsPage from './pages/LogsPage'
import GalleryPage from './pages/GalleryPage'
import GuidePage from './pages/GuidePage'
import SettingsPage from './pages/SettingsPage'

const NAV: { to: string; icon: typeof LayoutDashboard; labelKey: TranslationKey; exact: boolean; badge?: string }[] = [
  { to: '/', icon: Clapperboard, labelKey: 'nav.studioHub', exact: true, badge: '4 XƯỞNG' },
  { to: '/dashboard', icon: LayoutDashboard, labelKey: 'nav.dashboard', exact: true },
  { to: '/projects', icon: FolderOpen, labelKey: 'nav.projects', exact: false },
  { to: '/gallery', icon: Film, labelKey: 'nav.gallery', exact: false },
  { to: '/logs', icon: ScrollText, labelKey: 'nav.logs', exact: false },
  { to: '/guide', icon: BookOpen, labelKey: 'nav.guide', exact: false },
  { to: '/settings', icon: SlidersHorizontal, labelKey: 'nav.settings', exact: false },
]

const BREADCRUMB_TAB_KEY: Record<string, TranslationKey> = {
  overview: 'app.breadcrumbTab.overview',
  characters: 'app.breadcrumbTab.characters',
  videos: 'app.breadcrumbTab.videos',
  pipeline: 'app.breadcrumbTab.pipeline',
}

function useClock() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return now
}

function useBreadcrumbs() {
  const { t } = useTranslation()
  const loc = useLocation()
  const { id } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const [projectName, setProjectName] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    fetchAPI<Project>(`/api/projects/${id}`).then(p => setProjectName(p.name)).catch(() => setProjectName(null))
  }, [id])

  const crumbs: string[] = []
  if (loc.pathname === '/') crumbs.push(t('nav.studioHub'))
  else if (loc.pathname === '/dashboard') crumbs.push(t('app.breadcrumb.dashboard'))
  else if (loc.pathname.startsWith('/projects')) {
    crumbs.push(t('app.breadcrumb.projects'))
    if (id) {
      crumbs.push(projectName ?? '…')
      const tab = searchParams.get('tab')
      const tabKey = tab ? BREADCRUMB_TAB_KEY[tab] : undefined
      if (tabKey) crumbs.push(t(tabKey))
    }
  } else if (loc.pathname.startsWith('/gallery')) crumbs.push(t('app.breadcrumb.gallery'))
  else if (loc.pathname.startsWith('/logs')) crumbs.push(t('app.breadcrumb.logs'))
  else if (loc.pathname.startsWith('/guide')) crumbs.push(t('app.breadcrumb.guide'))
  else if (loc.pathname.startsWith('/settings')) crumbs.push(t('app.breadcrumb.settings'))

  return crumbs
}

function LanguageSwitcher() {
  const { lang, setLang } = useTranslation()
  return (
    <select
      value={lang}
      onChange={e => setLang(e.target.value as Lang)}
      className="text-[10px] px-2.5 py-1.5 rounded-lg outline-none w-full bg-slate-50 border border-slate-200 text-slate-700 font-medium hover:border-pink-300 transition-colors"
    >
      {LANGS.map(l => (
        <option key={l} value={l}>{LANG_LABELS[l]}</option>
      ))}
    </select>
  )
}

function Sidebar() {
  const { t } = useTranslation()
  const { worker } = useWebSocketContext()
  const [health, setHealth] = useState<{ extension_connected: boolean } | null>(null)

  useEffect(() => {
    fetchAPI<{ extension_connected: boolean }>('/health').then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <aside className="w-56 flex-shrink-0 flex flex-col border-r bg-white/90 backdrop-blur-md z-20" style={{ borderColor: 'var(--border)' }}>
      {/* Brand Header */}
      <div className="px-4 py-4 flex items-center gap-2.5 border-b" style={{ borderColor: 'var(--border)' }}>
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-pink-500 via-rose-500 to-cyan-400 flex items-center justify-center text-white shadow-xs glow-primary">
          <Sparkles className="w-4 h-4 fill-white text-white" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1">
            <span className="text-xs font-black tracking-tight text-slate-900">OmniVideo</span>
            <span className="text-pink-500 text-xs font-bold">✦</span>
          </div>
          <span className="text-[9px] font-semibold text-pink-600 uppercase tracking-wider">Anime Studio Suite</span>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex flex-col gap-1 px-3 py-3">
        {NAV.map(({ to, icon: Icon, labelKey, exact, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className="flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all group"
            style={({ isActive }) => ({
              background: isActive ? 'rgba(255, 71, 126, 0.08)' : 'transparent',
              color: isActive ? '#e11d48' : '#64748b',
              border: isActive ? '1px solid rgba(255, 71, 126, 0.25)' : '1px solid transparent',
            })}
          >
            <div className="flex items-center gap-2.5">
              <Icon size={14} className="group-hover:scale-110 transition-transform" />
              <span>{t(labelKey)}</span>
            </div>
            {badge && (
              <span className="text-[9px] px-1.5 py-0.5 rounded-full font-bold bg-pink-500 text-white shadow-2xs">
                {badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom Telemetry Card */}
      <div className="mt-auto px-4 py-3.5 border-t flex flex-col gap-2.5 bg-slate-50/60" style={{ borderColor: 'var(--border)' }}>
        <LanguageSwitcher />
        <div className="flex items-center justify-between text-[11px] font-medium text-slate-500">
          <span>{t('app.workers')}</span>
          <span className="font-bold text-slate-800">{worker ? `${worker.active}/${worker.active + worker.slots}` : '1 / 5'}</span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-medium text-slate-600 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: health?.extension_connected ? '#10b981' : '#ef4444' }}
          />
          <span className="truncate">
            {health?.extension_connected ? t('app.extensionConnected') : health ? t('app.extensionDisconnected') : t('app.extensionChecking')}
          </span>
        </div>
      </div>
    </aside>
  )
}

function Header() {
  const { t } = useTranslation()
  const { isConnected } = useWebSocketContext()
  const crumbs = useBreadcrumbs()
  const clock = useClock()

  return (
    <header className="flex items-center gap-4 px-6 h-14 flex-shrink-0 border-b bg-white/80 backdrop-blur-md z-10" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
        <span className="text-pink-600 font-bold">{t('app.breadcrumbRoot')}</span>
        {crumbs.map((c, i) => (
          <span key={i} className="flex items-center gap-2">
            <span className="text-slate-300">/</span>
            <span className={i === crumbs.length - 1 ? 'text-slate-900 font-bold' : 'text-slate-500'}>{c}</span>
          </span>
        ))}
      </div>
      <span className="ml-auto" />
      <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
        <span className="font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md text-[11px]">
          {clock.toLocaleTimeString()}
        </span>
        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold border bg-white" style={{ borderColor: isConnected ? '#10b98133' : '#ef444433', color: isConnected ? '#059669' : '#dc2626' }}>
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: isConnected ? '#10b981' : '#ef4444', animation: isConnected ? 'pulse 2s ease-in-out infinite' : 'none' }}
          />
          {isConnected ? t('app.wsLive') : t('app.wsDisconnected')}
        </span>
      </div>
    </header>
  )
}

function Layout() {
  return (
    <div className="flex h-screen overflow-hidden porcelain-grid" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Routes>
            <Route path="/" element={<StudioHubPage />} />
            <Route path="/studio" element={<StudioHubPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:id" element={<ProjectsPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/guide" element={<GuidePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <WebSocketProvider>
          <TooltipProvider>
            <Layout />
          </TooltipProvider>
        </WebSocketProvider>
      </LanguageProvider>
    </BrowserRouter>
  )
}
