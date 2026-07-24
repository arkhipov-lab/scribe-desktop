import { useEffect, useRef, useState, type DragEvent } from "react";
import {
  formatElapsed,
  getApi,
  getDefaultState,
} from "./api";
import LanguageSelect from "./LanguageSelect";
import MarkdownBody from "./MarkdownBody";
import { DEFAULT_LANGUAGE } from "./languages";
import type { AppState, SummaryStatus } from "./vite-env";

const ACCEPTED = ".m4a,.mp3,.wav,.mp4,.mov";

type ResultTab = "transcript" | "summary";

function isBusy(status: AppState["status"]): boolean {
  return status === "loading_model" || status === "transcribing";
}

function isRecording(status: AppState["status"]): boolean {
  return status === "recording";
}

function isSummaryBusy(status: SummaryStatus): boolean {
  return status === "loading_model" || status === "summarizing";
}

function mergeState(next: AppState): AppState {
  return {
    status: next.status,
    message: next.message,
    file_path: next.file_path,
    file_name: next.file_name,
    language: next.language,
    transcript: next.transcript,
    summary: next.summary ?? "",
    summary_status: next.summary_status ?? "idle",
    summary_error: next.summary_error ?? null,
    error: next.error ?? null,
    elapsed_seconds: next.elapsed_seconds,
    started_at: next.started_at,
  };
}

export default function App() {
  const [state, setState] = useState<AppState>(getDefaultState);
  const [bridgeError, setBridgeError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const [appName, setAppName] = useState("Scribe");
  const [resultTab, setResultTab] = useState<ResultTab>("transcript");
  const copyTimer = useRef<number | null>(null);
  const lastTranscriptRef = useRef("");

  useEffect(() => {
    let cancelled = false;
    let intervalId = 0;

    async function boot() {
      try {
        const api = await getApi();
        if (cancelled) return;
        const [initial, info] = await Promise.all([
          api.get_state(),
          api.get_app_info?.().catch(() => null),
        ]);
        if (cancelled) return;
        setState(mergeState(initial));
        if (info?.app_name) setAppName(info.app_name);
        setBridgeError(null);

        intervalId = window.setInterval(async () => {
          try {
            const next = await api.get_state();
            if (!cancelled) setState(mergeState(next));
          } catch {
            // Keep last known state if a poll fails briefly.
          }
        }, 400);
      } catch (err) {
        if (!cancelled) {
          setBridgeError(
            err instanceof Error ? err.message : "Desktop bridge is not available.",
          );
        }
      }
    }

    void boot();
    return () => {
      cancelled = true;
      if (intervalId) window.clearInterval(intervalId);
      if (copyTimer.current) window.clearTimeout(copyTimer.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    // New transcript → always land on Transcript tab.
    if (state.transcript && state.transcript !== lastTranscriptRef.current) {
      setResultTab("transcript");
    }
    lastTranscriptRef.current = state.transcript;
  }, [state.transcript]);

  async function withApi(
    action: (api: Awaited<ReturnType<typeof getApi>>) => Promise<AppState>,
  ) {
    try {
      const api = await getApi();
      const next = await action(api);
      setState(mergeState(next));
      setBridgeError(null);
    } catch (err) {
      setBridgeError(
        err instanceof Error ? err.message : "Desktop bridge is not available.",
      );
    }
  }

  const busy = isBusy(state.status);
  const recording = isRecording(state.status);
  const summaryBusy = isSummaryBusy(state.summary_status);
  const locked = busy || recording;
  const canTranscribe = Boolean(state.file_path) && !locked;
  const language = state.language || DEFAULT_LANGUAGE;
  const activeText =
    resultTab === "summary" ? state.summary : state.transcript;
  const canCopy = Boolean(activeText);

  async function onSelectFile() {
    await withApi((api) => api.select_file());
  }

  async function onSaveAudioCopy() {
    await withApi((api) => api.save_audio_copy());
  }

  async function onLanguageChange(next: string) {
    await withApi((api) => api.set_language(next));
  }

  async function onTranscribe() {
    setResultTab("transcript");
    await withApi((api) => api.start_transcription());
  }

  async function onCancel() {
    await withApi((api) => api.cancel_transcription());
  }

  async function onRecord() {
    await withApi((api) => api.start_recording());
  }

  async function onStopRecord() {
    await withApi((api) => api.stop_recording());
  }

  async function onSummarize() {
    await withApi((api) => api.start_summary());
  }

  async function onCancelSummary() {
    await withApi((api) => api.cancel_summary());
  }

  async function onCopy() {
    const text = activeText;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      if (copyTimer.current) window.clearTimeout(copyTimer.current);
      copyTimer.current = window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // Fallback for environments without clipboard permissions
      const area = document.createElement("textarea");
      area.value = text;
      area.style.position = "fixed";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      document.body.removeChild(area);
      setCopied(true);
      if (copyTimer.current) window.clearTimeout(copyTimer.current);
      copyTimer.current = window.setTimeout(() => setCopied(false), 1600);
    }
  }

  function onDragOver(e: DragEvent) {
    e.preventDefault();
    if (!locked) setDragging(true);
  }

  function onDragLeave(e: DragEvent) {
    e.preventDefault();
    // Only clear highlight when leaving the dropzone itself.
    const related = e.relatedTarget as Node | null;
    if (related && e.currentTarget instanceof Node && e.currentTarget.contains(related)) {
      return;
    }
    setDragging(false);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    // File path is applied by the Python/pywebview native drop handler.
    // Do not stopPropagation — otherwise the native listener never sees the drop.
  }

  const showResult =
    state.status === "completed" ||
    (Boolean(state.transcript) && state.status !== "error");

  const summaryBanner = state.summary_error;

  return (
    <div className="app">
      <header className="header">
        <p className="brand">{appName}</p>
        <h1>Notes, ready to share</h1>
        <p className="subtitle">
          Record a call or drop a file — get a clean transcript in minutes.
        </p>
      </header>

      {(bridgeError || state.error || summaryBanner) && (
        <div className="banner error" role="alert">
          {bridgeError || state.error || summaryBanner}
        </div>
      )}

      <section className="panel">
        <h2>File</h2>
        {recording ? (
          <div className="record-active" aria-live="polite">
            <div className="record-active-meta">
              <span className="record-pulse" aria-hidden="true" />
              <div>
                <p className="record-active-title">Recording</p>
                <p className="record-active-hint">Microphone + system audio</p>
              </div>
            </div>
            <p className="record-timer">{formatElapsed(state.elapsed_seconds)}</p>
            <button
              type="button"
              className="btn stop-record"
              onClick={() => void onStopRecord()}
              aria-label="Stop recording"
            >
              <span className="stop-square" aria-hidden="true" />
              Stop
            </button>
          </div>
        ) : (
          <div
            id="file-dropzone"
            className={`dropzone ${dragging ? "dragging" : ""} ${locked ? "disabled" : ""}`}
            onDragOver={onDragOver}
            onDragEnter={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={(e) => void onDrop(e)}
          >
            <p className="drop-title">
              {state.file_name ? state.file_name : "Drop audio or video here"}
            </p>
            <p className="drop-hint">Supported: {ACCEPTED.replaceAll(",", " ")}</p>
            <div className="drop-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => void onSelectFile()}
                disabled={locked}
              >
                Select file
              </button>
              {state.file_path && (
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => void onSaveAudioCopy()}
                  disabled={locked}
                >
                  Save copy
                </button>
              )}
              <button
                type="button"
                className="btn record"
                onClick={() => void onRecord()}
                disabled={locked}
                aria-label="Record audio"
              >
                <span className="record-dot" aria-hidden="true" />
                Record
              </button>
            </div>
          </div>
        )}
      </section>

      <section className="panel row">
        <div className="field">
          <h2>Language</h2>
          <label className="sr-only" htmlFor="language-select">
            Language
          </label>
          <LanguageSelect
            value={language}
            disabled={locked}
            onChange={(next) => void onLanguageChange(next)}
          />
        </div>

        <div className="actions">
          <button
            type="button"
            className="btn primary"
            disabled={!canTranscribe}
            onClick={() => void onTranscribe()}
          >
            Transcribe
          </button>
          {busy && (
            <button
              type="button"
              className="btn ghost"
              onClick={() => void onCancel()}
            >
              Cancel
            </button>
          )}
        </div>
      </section>

      <section className="panel status-panel">
        <div className="status-row">
          <div className="status-left">
            {(busy || recording || summaryBusy) && (
              <span className="spinner" aria-hidden="true" />
            )}
            <div>
              <p className="status-label">{statusLabel(state.status, state.summary_status)}</p>
              <p className="status-message">{state.message}</p>
            </div>
          </div>
          <p className="elapsed" aria-live="polite">
            {formatElapsed(state.elapsed_seconds)}
          </p>
        </div>
        {(busy || recording || summaryBusy) && (
          <div
            className="progress indeterminate"
            role="progressbar"
            aria-valuetext={
              recording ? "Recording" : summaryBusy ? "Summarizing" : "Processing"
            }
          >
            <div className="bar" />
          </div>
        )}
      </section>

      {showResult && (
        <section className="panel result-panel">
          <div className="result-header">
            <div className="result-tabs" role="tablist" aria-label="Result">
              <button
                type="button"
                role="tab"
                aria-selected={resultTab === "transcript"}
                className={`result-tab ${resultTab === "transcript" ? "active" : ""}`}
                onClick={() => setResultTab("transcript")}
              >
                Transcript
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={resultTab === "summary"}
                className={`result-tab ${resultTab === "summary" ? "active" : ""}`}
                onClick={() => setResultTab("summary")}
              >
                Summary
              </button>
            </div>
            <div className="result-actions">
              {resultTab === "summary" && summaryBusy && (
                <button
                  type="button"
                  className="btn ghost"
                  onClick={() => void onCancelSummary()}
                >
                  Cancel
                </button>
              )}
              {resultTab === "summary" &&
                !summaryBusy &&
                state.summary_status !== "completed" &&
                Boolean(state.transcript) && (
                  <button
                    type="button"
                    className="btn ghost"
                    onClick={() => void onSummarize()}
                  >
                    Generate summary
                  </button>
                )}
              {resultTab === "summary" &&
                state.summary_status === "completed" &&
                !summaryBusy && (
                  <button
                    type="button"
                    className="btn ghost"
                    onClick={() => void onSummarize()}
                  >
                    Regenerate
                  </button>
                )}
              <button
                type="button"
                className="btn secondary"
                onClick={() => void onCopy()}
                disabled={!canCopy}
              >
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>

          {resultTab === "transcript" ? (
            <MarkdownBody
              content={state.transcript}
              emptyLabel="Transcript will appear here."
            />
          ) : summaryBusy ? (
            <div className="summary-empty" aria-live="polite">
              <div className="summary-busy">
                <span className="spinner" aria-hidden="true" />
                <p>
                  {state.summary_status === "loading_model"
                    ? "Loading summary model…"
                    : "Writing summary…"}
                </p>
              </div>
            </div>
          ) : state.summary ? (
            <MarkdownBody
              content={state.summary}
              emptyLabel="Summary will appear here."
            />
          ) : (
            <div className="summary-empty">
              <p>
                {state.summary_status === "error"
                  ? "Summary failed. You can try again."
                  : "Summary will appear here after transcription finishes."}
              </p>
              {Boolean(state.transcript) && (
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => void onSummarize()}
                >
                  Generate summary
                </button>
              )}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function statusLabel(
  status: AppState["status"],
  summaryStatus: SummaryStatus,
): string {
  if (status === "completed" && isSummaryBusy(summaryStatus)) {
    return summaryStatus === "loading_model"
      ? "Loading summary model"
      : "Summarizing";
  }
  switch (status) {
    case "idle":
      return "Idle";
    case "ready":
      return "Ready";
    case "recording":
      return "Recording";
    case "loading_model":
      return "Loading model";
    case "transcribing":
      return "Transcribing";
    case "completed":
      return "Completed";
    case "error":
      return "Error";
    default:
      return status;
  }
}
