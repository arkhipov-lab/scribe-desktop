/// <reference types="vite/client" />

export type AppStatus =
  | "idle"
  | "ready"
  | "recording"
  | "loading_model"
  | "transcribing"
  | "completed"
  | "error";

export type SummaryStatus =
  | "idle"
  | "loading_model"
  | "summarizing"
  | "completed"
  | "error";

export type SummaryLength = "short" | "normal" | "detailed";

export type LanguageCode = string;

export interface AppState {
  status: AppStatus;
  message: string;
  file_path: string | null;
  file_name: string | null;
  language: LanguageCode | string;
  transcript: string;
  summary: string;
  summary_status: SummaryStatus;
  summary_error: string | null;
  error: string | null;
  elapsed_seconds: number;
  started_at: number | null;
  summary_preset: string;
  additional_instructions: string;
  summary_length: SummaryLength | string;
  auto_summary: boolean;
  whisper_model: string;
  summary_model: string;
  performance_tier?: string | null;
  hardware_reason?: string | null;
  session_id?: string | null;
  session_title?: string | null;
  history_sidebar_open?: boolean;
}

export interface ApiResult extends AppState {
  ok?: boolean;
  cancelled?: boolean;
}

export interface LanguageOption {
  code: string;
  label: string;
}

export interface SummaryPresetOption {
  id: string;
  label: string;
}

export interface ModelOption {
  id: string;
  label: string;
  hint?: string;
  huggingface_id?: string;
}

export interface HistorySession {
  id: string;
  title: string;
  created_at?: string | null;
  updated_at?: string | null;
  source_name?: string | null;
  has_audio?: boolean;
  has_transcript?: boolean;
  has_summary?: boolean;
  language?: string | null;
}

export interface AppSettings {
  language: string;
  summary_preset: string;
  additional_instructions: string;
  summary_length: SummaryLength | string;
  auto_summary: boolean;
  whisper_model: string;
  summary_model: string;
  history_sidebar_open?: boolean;
}

export interface AppInfo {
  app_name: string;
  version: string;
  whisper_model: string;
  summary_model: string;
  performance_tier?: string;
  hardware_reason?: string;
}

export interface PywebviewApi {
  get_state: () => Promise<AppState>;
  select_file: () => Promise<ApiResult>;
  save_audio_copy: () => Promise<ApiResult>;
  get_playback_src: () => Promise<{
    ok: boolean;
    error?: string;
    mime?: string;
    data_base64?: string;
    size?: number;
  }>;
  export_notes: () => Promise<ApiResult>;
  set_file_path: (filePath: string) => Promise<ApiResult>;
  set_language: (language: string) => Promise<ApiResult>;
  get_languages: () => Promise<LanguageOption[]>;
  get_summary_presets: () => Promise<SummaryPresetOption[]>;
  get_whisper_models: () => Promise<ModelOption[]>;
  get_summary_models: () => Promise<ModelOption[]>;
  get_hardware_info: () => Promise<{
    memory_gb: number | null;
    chip_generation: number | null;
    chip_name: string | null;
    tier: string;
    reason: string;
  }>;
  get_settings: () => Promise<AppSettings>;
  update_settings: (patch: Partial<AppSettings>) => Promise<ApiResult>;
  list_sessions: () => Promise<HistorySession[]>;
  open_session: (sessionId: string) => Promise<ApiResult>;
  delete_session: (sessionId: string) => Promise<ApiResult>;
  start_transcription: () => Promise<ApiResult>;
  cancel_transcription: () => Promise<ApiResult>;
  start_summary: () => Promise<ApiResult>;
  cancel_summary: () => Promise<ApiResult>;
  start_recording: () => Promise<ApiResult>;
  stop_recording: () => Promise<ApiResult>;
  clear_result: () => Promise<ApiResult>;
  reset_for_another_file: () => Promise<ApiResult>;
  check_ffmpeg: () => Promise<{ ok: boolean; path: string | null; message: string }>;
  get_model_name: () => Promise<string>;
  get_summary_model_name: () => Promise<string>;
  get_app_info: () => Promise<AppInfo>;
}

declare global {
  interface Window {
    pywebview?: {
      api: PywebviewApi;
    };
  }

  interface File {
    /** Non-standard path exposed by some desktop WebViews */
    path?: string;
  }
}

export {};
