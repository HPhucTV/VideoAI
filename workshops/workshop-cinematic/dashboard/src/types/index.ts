// Enums
export type RequestType = 'GENERATE_IMAGE' | 'REGENERATE_IMAGE' | 'EDIT_IMAGE' | 'GENERATE_VIDEO' | 'REGENERATE_VIDEO' | 'GENERATE_VIDEO_REFS' | 'UPSCALE_VIDEO' | 'GENERATE_CHARACTER_IMAGE' | 'REGENERATE_CHARACTER_IMAGE' | 'EDIT_CHARACTER_IMAGE'
export type StatusType = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
export type Orientation = 'VERTICAL' | 'HORIZONTAL'
export type ChainType = 'ROOT' | 'CONTINUATION' | 'INSERT'
export type EntityType = 'character' | 'location' | 'creature' | 'visual_asset' | 'generic_troop' | 'faction'
export type ProjectStatus = 'ACTIVE' | 'ARCHIVED' | 'DELETED'

// Models — match the Python models exactly
export interface Project {
  id: string
  name: string
  description: string | null
  story: string | null
  thumbnail_url: string | null
  language: string
  status: ProjectStatus
  user_paygate_tier: string | null
  material: string
  narrator_voice: string | null
  narrator_ref_audio: string | null
  created_at: string
  updated_at: string
}

export interface Character {
  id: string
  name: string
  entity_type: EntityType
  description: string | null
  image_prompt: string | null
  voice_description: string | null
  reference_image_url: string | null
  media_id: string | null
  created_at: string
  updated_at: string
}

export interface Video {
  id: string
  project_id: string
  title: string
  description: string | null
  display_order: number
  status: string
  vertical_url: string | null
  horizontal_url: string | null
  thumbnail_url: string | null
  duration: number | null
  resolution: string | null
  created_at: string
  updated_at: string
}

export interface Scene {
  id: string
  video_id: string
  display_order: number
  prompt: string | null
  image_prompt: string | null
  video_prompt: string | null
  character_names: string | null  // JSON string array
  parent_scene_id: string | null
  chain_type: ChainType
  source: string | null
  vertical_image_url: string | null
  vertical_image_media_id: string | null
  vertical_image_status: StatusType
  vertical_video_url: string | null
  vertical_video_media_id: string | null
  vertical_video_status: StatusType
  vertical_upscale_url: string | null
  vertical_upscale_media_id: string | null
  vertical_upscale_status: StatusType
  horizontal_image_url: string | null
  horizontal_image_media_id: string | null
  horizontal_image_status: StatusType
  horizontal_video_url: string | null
  horizontal_video_media_id: string | null
  horizontal_video_status: StatusType
  horizontal_upscale_url: string | null
  horizontal_upscale_media_id: string | null
  horizontal_upscale_status: StatusType
  narrator_text: string | null
  trim_start: number | null
  trim_end: number | null
  duration: number | null
  created_at: string
  updated_at: string
}

export interface Request {
  id: string
  project_id: string | null
  video_id: string | null
  scene_id: string | null
  character_id: string | null
  type: RequestType
  orientation: Orientation | null
  status: StatusType
  request_id: string | null
  media_id: string | null
  output_url: string | null
  error_message: string | null
  retry_count: number
  created_at: string
  updated_at: string
}

// WebSocket event
export interface WSEvent {
  type: string
  data: Record<string, unknown>
  timestamp: string
}

// AI video review — match agent/models/review.py exactly
export interface DimensionScores {
  character_consistency: number
  prompt_adherence: number
  motion_quality: number
  visual_fidelity: number
  temporal_coherence: number
  composition: number
}

export interface VideoError {
  severity: string // CRITICAL / HIGH / MINOR
  time_range: string
  description: string
}

export interface SegmentScore {
  time_range: string
  score: number
}

export interface SceneReview {
  scene_id: string
  overall_score: number
  verdict: string // excellent / good / acceptable / poor / unusable
  dimensions: DimensionScores
  errors: VideoError[]
  usable_segments: SegmentScore[]
  fix_guide: string
  frames_analyzed: number
  fps_used: number
  has_critical_errors: boolean
}

// AI provider settings — match the /api/providers payload exactly
export interface RoleAssignment {
  provider: string
  model: string | null
  effort: string | null
}

export interface RoleMeta {
  label: string
  description: string
}

export interface ProviderInfo {
  binary: string
  installed: boolean
  tested: boolean | null
  error: string | null
  efforts: string[]
  default_model: string | null
  catalog_is_authoritative: boolean
  model_encodes_effort: boolean
}

export interface ProvidersResponse {
  active: string
  roles: Record<string, RoleAssignment>
  role_meta: Record<string, RoleMeta>
  providers: Record<string, ProviderInfo>
}

export interface ProviderModel {
  id: string
  label: string
}

export interface ProviderModelsResponse {
  provider: string
  models: ProviderModel[]
  authoritative: boolean
}

export interface ProvidersUpdateResponse {
  status: string
  active: string
  roles: Record<string, RoleAssignment>
}

// ─── Studio 4 Workshops Unified Models ─────────────────────────
export interface StudioVideo {
  id: string
  filename: string
  title: string
  workshop: 'news' | 'explainer' | 'whiteboard' | 'cinematic'
  workshop_name: string
  workshop_color: string
  aspect_ratio: string
  size_bytes: number
  size_formatted: string
  created_at: string
  timestamp: number
  has_thumbnail: boolean
  thumb_url: string | null
  video_url: string
  has_srt: boolean
  srt_url: string | null
  metadata?: Record<string, any>
}

export interface StudioJobStep {
  id: string
  label: string
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  detail: string
}

export interface StudioJob {
  id: string
  workshop: 'news' | 'explainer' | 'whiteboard' | 'cinematic'
  workshop_name: string
  title: string
  status: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'FAILED'
  progress: number
  current_step: string
  started_at: number
  updated_at: number
  completed_at?: number
  steps: StudioJobStep[]
  log_lines: string[]
  error?: string
  output_video_path?: string
}

export interface WorkshopStorageStat {
  id: string
  name: string
  color: string
  size_bytes: number
  size_formatted: string
}

export interface StudioStorage {
  workshops: Record<string, WorkshopStorageStat>
  total_workshops_bytes: number
  total_workshops_formatted: string
  disk: {
    total_bytes: number
    total_formatted: string
    free_bytes: number
    free_formatted: string
    used_bytes: number
    used_formatted: string
    free_percent: number
  }
}

export interface PublishingTitleVariant {
  id: string
  label: string
  badge_color: 'pink' | 'cyan' | 'amber' | string
  metrics?: string
  text: string
}

export interface PublishingKit {
  video_id?: string
  project_id?: string
  status: 'ready' | 'drafting' | 'empty' | string
  updated_at?: string
  sync_note: string
  titles: PublishingTitleVariant[]
  caption: string
  hashtags: string[]
  thumbnail_url?: string | null
  thumbnail_score?: string
  thumbnail_specs?: string
}
