import type { AppState, PywebviewApi } from "./vite-env";
import { DEFAULT_LANGUAGE } from "./languages";

const DEFAULT_STATE: AppState = {
  status: "idle",
  message: "Drop an audio file, select a file, or record notes.",
  file_path: null,
  file_name: null,
  language: DEFAULT_LANGUAGE,
  transcript: "",
  summary: "",
  summary_status: "idle",
  summary_error: null,
  error: null,
  elapsed_seconds: 0,
  started_at: null,
};

function waitForApi(timeoutMs = 15000): Promise<PywebviewApi> {
  return new Promise((resolve, reject) => {
    const started = Date.now();

    const tryResolve = () => {
      const api = window.pywebview?.api;
      if (api) {
        resolve(api);
        return true;
      }
      return false;
    };

    if (tryResolve()) {
      return;
    }

    const onReady = () => {
      if (tryResolve()) {
        window.removeEventListener("pywebviewready", onReady);
      }
    };
    window.addEventListener("pywebviewready", onReady);

    const interval = window.setInterval(() => {
      if (tryResolve()) {
        window.clearInterval(interval);
        window.removeEventListener("pywebviewready", onReady);
        return;
      }
      if (Date.now() - started > timeoutMs) {
        window.clearInterval(interval);
        window.removeEventListener("pywebviewready", onReady);
        reject(new Error("Desktop bridge is not available."));
      }
    }, 50);
  });
}

let apiPromise: Promise<PywebviewApi> | null = null;

export function getApi(): Promise<PywebviewApi> {
  if (!apiPromise) {
    apiPromise = waitForApi();
  }
  return apiPromise;
}

export function getDefaultState(): AppState {
  return { ...DEFAULT_STATE };
}

export function formatElapsed(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}
