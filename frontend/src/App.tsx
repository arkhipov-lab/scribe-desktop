import { useEffect, useRef, useState, type DragEvent } from "react";
import {
  formatElapsed,
  getApi,
  getDefaultState,
  resetApi,
} from "./api";
import LanguageSelect from "./LanguageSelect";
import MarkdownBody from "./MarkdownBody";
import PresetSelect from "./PresetSelect";
import {
  IconCheck,
  IconCopy,
  IconExport,
  IconRefresh,
  IconSave,
  IconSparkles,
} from "./icons";
import { DEFAULT_LANGUAGE } from "./languages";
import type {
  AppState,
  HistorySession,
  ModelOption,
  SummaryLength,
  SummaryPresetOption,
  SummaryStatus,
} from "./vite-env";

const ACCEPTED = ".m4a,.mp3,.wav,.mp4,.mov";

const LENGTH_OPTIONS: { id: SummaryLength; label: string }[] = [
  { id: "short", label: "Short" },
  { id: "normal", label: "Normal" },
  { id: "detailed", label: "Detailed" },
];

const FALLBACK_PRESETS: SummaryPresetOption[] = [
  { id: "meeting_notes", label: "Meeting notes" },
  { id: "action_items", label: "Action items only" },
  { id: "executive", label: "Executive summary" },
  { id: "customer_interview", label: "Customer interview" },
  { id: "lecture", label: "Lecture / research notes" },
  { id: "cleaned_transcript", label: "Cleaned transcript" },
];

const FALLBACK_WHISPER: ModelOption[] = [
  { id: "small", label: "Small", hint: "Faster, lower memory" },
  { id: "medium", label: "Medium", hint: "Better accuracy, more memory" },
];

const FALLBACK_SUMMARY_MODELS: ModelOption[] = [
  { id: "1.5b", label: "1.5B", hint: "Lighter notes model" },
  { id: "3b", label: "3B", hint: "Higher-quality notes" },
];

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
    summary_preset: next.summary_preset ?? "meeting_notes",
    additional_instructions: next.additional_instructions ?? "",
    summary_length: next.summary_length ?? "normal",
    auto_summary: next.auto_summary ?? true,
    whisper_model: next.whisper_model ?? "medium",
    summary_model: next.summary_model ?? "3b",
    performance_tier: next.performance_tier ?? null,
    hardware_reason: next.hardware_reason ?? null,
    session_id: next.session_id ?? null,
    session_title: next.session_title ?? null,
    history_sidebar_open: next.history_sidebar_open ?? true,
  };
}

export default function App() {
  const [state, setState] = useState<AppState>(getDefaultState);
  const [bridgeError, setBridgeError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState(false);
  const [resultTab, setResultTab] = useState<ResultTab>("transcript");
  const [presets, setPresets] = useState<SummaryPresetOption[]>(FALLBACK_PRESETS);
  const [whisperModels, setWhisperModels] = useState<ModelOption[]>(FALLBACK_WHISPER);
  const [summaryModels, setSummaryModels] =
    useState<ModelOption[]>(FALLBACK_SUMMARY_MODELS);
  const [instructionsDraft, setInstructionsDraft] = useState("");
  const [summaryOptionsOpen, setSummaryOptionsOpen] = useState(false);
  const [sessions, setSessions] = useState<HistorySession[]>([]);
  const copyTimer = useRef<number | null>(null);
  const exportTimer = useRef<number | null>(null);
  const instructionsTimer = useRef<number | null>(null);
  const lastTranscriptRef = useRef("");

  useEffect(() => {
    let cancelled = false;
    let intervalId = 0;

    async function boot() {
      try {
        const api = await getApi();
        if (cancelled) return;
        const [initial, presetList, whisperList, summaryList] = await Promise.all([
          api.get_state(),
          api.get_summary_presets
            ? api.get_summary_presets().catch(() => FALLBACK_PRESETS)
            : Promise.resolve(FALLBACK_PRESETS),
          api.get_whisper_models
            ? api.get_whisper_models().catch(() => FALLBACK_WHISPER)
            : Promise.resolve(FALLBACK_WHISPER),
          api.get_summary_models
            ? api.get_summary_models().catch(() => FALLBACK_SUMMARY_MODELS)
            : Promise.resolve(FALLBACK_SUMMARY_MODELS),
        ]);
        if (cancelled) return;
        const merged = mergeState(initial);
        setState(merged);
        setInstructionsDraft(merged.additional_instructions);
        if (Array.isArray(presetList) && presetList.length > 0) {
          setPresets(presetList);
        }
        if (Array.isArray(whisperList) && whisperList.length > 0) {
          setWhisperModels(whisperList);
        }
        if (Array.isArray(summaryList) && summaryList.length > 0) {
          setSummaryModels(summaryList);
        }
        if (api.list_sessions) {
          try {
            const items = await api.list_sessions();
            if (!cancelled && Array.isArray(items)) setSessions(items);
          } catch {
            // History optional on older bridges.
          }
        }
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
      if (exportTimer.current) window.clearTimeout(exportTimer.current);
      if (instructionsTimer.current) window.clearTimeout(instructionsTimer.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function retryBridge() {
    resetApi();
    window.location.reload();
  }

  useEffect(() => {
    // New transcript → always land on Transcript tab.
    if (state.transcript && state.transcript !== lastTranscriptRef.current) {
      setResultTab("transcript");
    }
    lastTranscriptRef.current = state.transcript;
  }, [state.transcript]);

  useEffect(() => {
    // Keep draft aligned when settings load/change from the bridge (not while typing).
    if (document.activeElement?.id === "summary-instructions") return;
    setInstructionsDraft(state.additional_instructions || "");
  }, [state.additional_instructions]);

  useEffect(() => {
    let cancelled = false;
    async function refresh() {
      try {
        const api = await getApi();
        if (!api.list_sessions || cancelled) return;
        const items = await api.list_sessions();
        if (!cancelled && Array.isArray(items)) setSessions(items);
      } catch {
        // Bridge may be briefly unavailable during reload.
      }
    }
    void refresh();
    return () => {
      cancelled = true;
    };
  }, [state.session_id, state.session_title, state.summary_status, state.status]);

  async function withApi(
    action: (api: Awaited<ReturnType<typeof getApi>>) => Promise<AppState>,
  ) {
    try {
      const api = await getApi();
      const next = await action(api);
      const merged = mergeState(next);
      setState(merged);
      setBridgeError(null);
      return merged;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Desktop bridge is not available.";
      if (message.includes("Desktop bridge is not available")) {
        resetApi();
      }
      setBridgeError(message);
      return null;
    }
  }

  const busy = isBusy(state.status);
  const recording = isRecording(state.status);
  const summaryBusy = isSummaryBusy(state.summary_status);
  const locked = busy || recording;
  const canTranscribe = Boolean(state.file_path) && !locked;
  const language = state.language || DEFAULT_LANGUAGE;
  const hasTranscript = Boolean(state.transcript?.trim());
  const audioLocked = hasTranscript;
  const activeText =
    resultTab === "summary" ? state.summary : state.transcript;
  const canCopy = Boolean(activeText);
  const canExport = Boolean(state.transcript?.trim() || state.summary?.trim());
  const summaryLength = (state.summary_length || "normal") as SummaryLength;

  async function onSelectFile() {
    await withApi((api) => api.select_file());
  }

  async function onSaveAudioCopy() {
    await withApi((api) => api.save_audio_copy());
  }

  async function onExportNotes() {
    try {
      const api = await getApi();
      if (!api.export_notes) {
        setBridgeError("Export is not available in this build. Rebuild the app.");
        return;
      }
      const next = await api.export_notes();
      setState(mergeState(next));
      setBridgeError(null);
      if (next.ok) {
        setExported(true);
        if (exportTimer.current) window.clearTimeout(exportTimer.current);
        exportTimer.current = window.setTimeout(() => setExported(false), 1600);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Desktop bridge is not available.";
      if (message.includes("Desktop bridge is not available")) {
        resetApi();
      }
      setBridgeError(message);
    }
  }

  async function onLanguageChange(next: string) {
    await withApi((api) => api.set_language(next));
  }

  async function onSettingsPatch(
    patch: Partial<{
      summary_preset: string;
      additional_instructions: string;
      summary_length: SummaryLength;
      auto_summary: boolean;
      whisper_model: string;
      summary_model: string;
    }>,
  ) {
    await withApi((api) => api.update_settings(patch));
  }

  async function onOpenSession(sessionId: string) {
    await withApi((api) => api.open_session(sessionId));
    setResultTab("transcript");
  }

  async function onNewTranscript() {
    if (!state.session_id && !state.file_path && !state.transcript) {
      setResultTab("transcript");
      return;
    }
    await withApi((api) => api.reset_for_another_file());
    setResultTab("transcript");
  }

  async function onDeleteSession(sessionId: string) {
    const label =
      sessions.find((s) => s.id === sessionId)?.title || "this session";
    if (!window.confirm(`Delete “${label}” from history?`)) return;
    await withApi((api) => api.delete_session(sessionId));
    try {
      const api = await getApi();
      if (api.list_sessions) {
        const items = await api.list_sessions();
        if (Array.isArray(items)) setSessions(items);
      }
    } catch {
      // ignore
    }
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

  function onInstructionsChange(value: string) {
    setInstructionsDraft(value);
    if (instructionsTimer.current) window.clearTimeout(instructionsTimer.current);
    instructionsTimer.current = window.setTimeout(() => {
      void onSettingsPatch({ additional_instructions: value });
    }, 450);
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
    if (!locked && !audioLocked) setDragging(true);
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
  const pageTitle = (state.session_title || "").trim() || "New Transcript";
  const isNewTranscript = !state.session_id;

  return (
    <div className="shell">
      <aside className="history-sidebar" aria-label="Session history">
        <div className="history-sidebar-inner">
          <button
            type="button"
            className={`history-new ${isNewTranscript ? "active" : ""}`}
            disabled={locked || summaryBusy}
            onClick={() => void onNewTranscript()}
          >
            New Transcript
          </button>
          <div className="history-list">
            {sessions.length === 0 ? (
              <p className="history-empty">History will appear here</p>
            ) : (
              sessions.map((session) => {
                const active = session.id === state.session_id;
                return (
                  <div
                    key={session.id}
                    className={`history-item ${active ? "active" : ""}`}
                  >
                    <button
                      type="button"
                      className="history-item-main"
                      disabled={locked || summaryBusy}
                      onClick={() => void onOpenSession(session.id)}
                    >
                      <span className="history-item-title">
                        {session.title || "New Transcript"}
                      </span>
                    </button>
                    <button
                      type="button"
                      className="history-item-delete"
                      disabled={locked || summaryBusy}
                      aria-label={`Delete ${session.title || "session"}`}
                      onClick={() => void onDeleteSession(session.id)}
                    >
                      ×
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </aside>

      <div className="app">
      <header className="header">
        <h1 className="page-title">{pageTitle}</h1>
      </header>

      {(bridgeError || state.error || summaryBanner) && (
        <div className="banner error" role="alert">
          <div className="banner-row">
            <span>{bridgeError || state.error || summaryBanner}</span>
            {bridgeError && (
              <button
                type="button"
                className="btn ghost banner-retry"
                onClick={() => retryBridge()}
              >
                Retry
              </button>
            )}
          </div>
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
        ) : audioLocked ? (
          <div className="file-locked">
            <div className="file-locked-meta">
              <p className="file-locked-name">
                {state.file_name || "Audio on file"}
              </p>
            </div>
            {state.file_path && (
              <button
                type="button"
                className="btn secondary icon-btn"
                onClick={() => void onSaveAudioCopy()}
                disabled={locked}
                title="Save copy"
                aria-label="Save copy"
              >
                <IconSave />
              </button>
            )}
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
            <p className="drop-hint">
              Supported: {ACCEPTED.replaceAll(",", " ")}
            </p>
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
                  className="btn secondary icon-btn"
                  onClick={() => void onSaveAudioCopy()}
                  disabled={locked}
                  title="Save copy"
                  aria-label="Save copy"
                >
                  <IconSave />
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
            disabled={locked || summaryBusy}
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

      <section
        className={`panel summary-settings ${summaryOptionsOpen ? "expanded" : "collapsed"}`}
      >
        <button
          type="button"
          className="disclosure-toggle"
          aria-expanded={summaryOptionsOpen}
          aria-controls="summary-options-body"
          onClick={() => setSummaryOptionsOpen((open) => !open)}
        >
          <span className="disclosure-copy">
            <span className="disclosure-title">Processing options</span>
            <span className="disclosure-hint">
              Models, summary style, and auto-summary
            </span>
          </span>
          <span className="disclosure-chevron" aria-hidden="true" />
        </button>

        {summaryOptionsOpen && (
          <div id="summary-options-body" className="summary-settings-body">
            {state.hardware_reason && (
              <p className="hardware-hint">
                Recommended for this Mac ({state.performance_tier || "auto"}):{" "}
                {state.hardware_reason}
              </p>
            )}

            <div className="summary-settings-grid">
              <div className="field">
                <label className="field-label" htmlFor="whisper-model">
                  Transcription model
                </label>
                <PresetSelect
                  value={state.whisper_model || "medium"}
                  options={whisperModels}
                  inputId="whisper-model"
                  ariaLabel="Transcription models"
                  searchPlaceholder="Search model…"
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ whisper_model: next })}
                />
              </div>

              <div className="field">
                <label className="field-label" htmlFor="summary-model">
                  Summary model
                </label>
                <PresetSelect
                  value={state.summary_model || "3b"}
                  options={summaryModels}
                  inputId="summary-model"
                  ariaLabel="Summary models"
                  searchPlaceholder="Search model…"
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ summary_model: next })}
                />
              </div>
            </div>

            <div className="summary-settings-grid">
              <div className="field">
                <label className="field-label" htmlFor="summary-preset">
                  Preset
                </label>
                <PresetSelect
                  value={state.summary_preset || "meeting_notes"}
                  options={presets}
                  inputId="summary-preset"
                  ariaLabel="Summary presets"
                  searchPlaceholder="Search preset…"
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ summary_preset: next })}
                />
              </div>

              <div className="field">
                <span className="field-label" id="summary-length-label">
                  Length
                </span>
                <div
                  className="segmented"
                  role="group"
                  aria-labelledby="summary-length-label"
                >
                  {LENGTH_OPTIONS.map((option) => (
                    <button
                      key={option.id}
                      type="button"
                      className={summaryLength === option.id ? "active" : ""}
                      disabled={locked || summaryBusy}
                      aria-pressed={summaryLength === option.id}
                      onClick={() => void onSettingsPatch({ summary_length: option.id })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="field instructions-field">
              <label className="field-label" htmlFor="summary-instructions">
                Additional instructions
              </label>
              <textarea
                id="summary-instructions"
                className="instructions-input"
                rows={2}
                maxLength={800}
                placeholder="e.g. highlight risks, keep technical terms in English"
                value={instructionsDraft}
                disabled={locked || summaryBusy}
                onChange={(e) => onInstructionsChange(e.target.value)}
              />
            </div>

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={Boolean(state.auto_summary)}
                disabled={locked || summaryBusy}
                onChange={(e) =>
                  void onSettingsPatch({ auto_summary: e.target.checked })
                }
              />
              <span>Auto-summarize after transcription</span>
            </label>
          </div>
        )}
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
                    className="btn ghost icon-btn"
                    onClick={() => void onSummarize()}
                    title="Generate summary"
                    aria-label="Generate summary"
                  >
                    <IconSparkles />
                  </button>
                )}
              {resultTab === "summary" &&
                state.summary_status === "completed" &&
                !summaryBusy && (
                  <button
                    type="button"
                    className="btn ghost icon-btn"
                    onClick={() => void onSummarize()}
                    title="Regenerate summary"
                    aria-label="Regenerate summary"
                  >
                    <IconRefresh />
                  </button>
                )}
              <button
                type="button"
                className="btn ghost icon-btn"
                onClick={() => void onExportNotes()}
                disabled={!canExport}
                title={exported ? "Exported" : "Export"}
                aria-label={exported ? "Exported" : "Export notes"}
              >
                {exported ? <IconCheck /> : <IconExport />}
              </button>
              <button
                type="button"
                className="btn secondary icon-btn"
                onClick={() => void onCopy()}
                disabled={!canCopy}
                title={copied ? "Copied" : "Copy"}
                aria-label={copied ? "Copied" : "Copy"}
              >
                {copied ? <IconCheck /> : <IconCopy />}
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
                  : state.auto_summary
                    ? "Summary will appear here after transcription finishes."
                    : "Auto-summary is off. Generate when you are ready."}
              </p>
              {Boolean(state.transcript) && (
                <button
                  type="button"
                  className="btn secondary icon-btn"
                  onClick={() => void onSummarize()}
                  title="Generate summary"
                  aria-label="Generate summary"
                >
                  <IconSparkles />
                </button>
              )}
            </div>
          )}
        </section>
      )}
    </div>
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
