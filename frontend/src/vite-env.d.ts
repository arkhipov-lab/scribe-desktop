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
}

export interface ApiResult extends AppState {
  ok?: boolean;
  cancelled?: boolean;
}

export interface LanguageOption {
  code: string;
  label: string;
}

export interface AppInfo {
  app_name: string;
  profile: string;
  version: string;
  whisper_model: string;
  summary_model: string;
}

export interface PywebviewApi {
  get_state: () => Promise<AppState>;
  select_file: () => Promise<ApiResult>;
  save_audio_copy: () => Promise<ApiResult>;
  set_file_path: (filePath: string) => Promise<ApiResult>;
  set_language: (language: string) => Promise<ApiResult>;
  get_languages: () => Promise<LanguageOption[]>;
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
