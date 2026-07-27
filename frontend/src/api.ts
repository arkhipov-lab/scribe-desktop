import type { AppState, PywebviewApi } from "./vite-env";
import { t } from "./i18n";
import { DEFAULT_LANGUAGE } from "./languages";

const DEFAULT_STATE: AppState = {
  status: "idle",
  message: "",
  file_path: null,
  file_name: null,
  language: DEFAULT_LANGUAGE,
  summary_language: DEFAULT_LANGUAGE,
  summary_language_persisted: false,
  transcript: "",
  summary: "",
  summary_status: "idle",
  summary_error: null,
  error: null,
  elapsed_seconds: 0,
  started_at: null,
  summary_preset: "meeting_notes",
  additional_instructions: "",
  summary_length: "normal",
  auto_summary: true,
  whisper_model: "medium",
  summary_model: "3b",
  performance_tier: null,
  hardware_reason: null,
  session_id: null,
  session_title: null,
  history_sidebar_open: true,
  used_language: null,
  used_summary_language: null,
  used_whisper_model: null,
  used_summary_model: null,
  used_summary_preset: null,
  used_summary_length: null,
  used_has_extra_instructions: false,
};

function waitForApi(timeoutMs = 20000): Promise<PywebviewApi> {
  return new Promise((resolve, reject) => {
    const started = Date.now();
    let settled = false;
    let interval = 0;

    const finish = (api: PywebviewApi) => {
      if (settled) return;
      settled = true;
      if (interval) window.clearInterval(interval);
      window.removeEventListener("pywebviewready", onReady);
      resolve(api);
    };

    const fail = () => {
      if (settled) return;
      settled = true;
      if (interval) window.clearInterval(interval);
      window.removeEventListener("pywebviewready", onReady);
      reject(new Error(t("errors.bridgeUnavailable")));
    };

    const tryResolve = () => {
      const api = window.pywebview?.api;
      if (api) {
        finish(api);
        return true;
      }
      return false;
    };

    const onReady = () => {
      tryResolve();
    };

    window.addEventListener("pywebviewready", onReady);

    if (tryResolve()) {
      return;
    }

    interval = window.setInterval(() => {
      if (tryResolve()) {
        return;
      }
      if (Date.now() - started > timeoutMs) {
        fail();
      }
    }, 50);
  });
}

let apiPromise: Promise<PywebviewApi> | null = null;

export function resetApi(): void {
  apiPromise = null;
}

export function getApi(): Promise<PywebviewApi> {
  if (!apiPromise) {
    apiPromise = waitForApi().catch((err) => {
      // Allow a later retry after a transient startup miss.
      apiPromise = null;
      throw err;
    });
  }
  return apiPromise;
}

export function getDefaultState(): AppState {
  return {
    ...DEFAULT_STATE,
    // Localized idle hint; backend replaces this after first poll.
    message: t("file.dropHere"),
  };
}

export function formatElapsed(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
