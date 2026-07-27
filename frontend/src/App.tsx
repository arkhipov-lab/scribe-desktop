import { useEffect, useRef, useState, type DragEvent } from "react";
import {
  formatElapsed,
  getApi,
  getDefaultState,
  resetApi,
} from "./api";
import { LOCALE_OPTIONS, getLocale, t, useI18n } from "./i18n";
import LanguageSelect from "./LanguageSelect";
import MarkdownBody from "./MarkdownBody";
import PresetSelect from "./PresetSelect";
import {
  IconCheck,
  IconCopy,
  IconExport,
  IconMonitor,
  IconMoon,
  IconPause,
  IconPlay,
  IconPlus,
  IconRefresh,
  IconSave,
  IconSparkles,
  IconStop,
  IconSun,
} from "./icons";
import { DEFAULT_LANGUAGE, isWhisperLanguage, languageLabel } from "./languages";
import { useTheme } from "./theme";
import type {
  AppState,
  HistorySession,
  ModelOption,
  SummaryLength,
  SummaryPresetOption,
  SummaryStatus,
} from "./vite-env";

const ACCEPTED = ".m4a,.mp3,.wav,.mp4,.mov";

type PlaybackState = "idle" | "playing" | "paused";

const LENGTH_IDS: SummaryLength[] = ["short", "normal", "detailed"];

const FALLBACK_PRESET_IDS = [
  "meeting_notes",
  "action_items",
  "executive",
  "customer_interview",
  "lecture",
  "cleaned_transcript",
] as const;

const FALLBACK_WHISPER_IDS = ["small", "medium"] as const;
const FALLBACK_SUMMARY_IDS = ["1.5b", "3b"] as const;

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

/** Map resolved UI locale (en/ru/…) to a Whisper summary language code. */
function summaryLanguageFromUiLocale(locale: string): string {
  const short = (locale || "").toLowerCase().split("-")[0] || DEFAULT_LANGUAGE;
  return isWhisperLanguage(short) ? short : DEFAULT_LANGUAGE;
}

function mergeState(next: AppState): AppState {
  return {
    status: next.status,
    message: next.message,
    file_path: next.file_path,
    file_name: next.file_name,
    language: next.language,
    summary_language: next.summary_language ?? next.language ?? DEFAULT_LANGUAGE,
    summary_language_persisted: Boolean(next.summary_language_persisted),
    transcript: next.transcript,
    transcript_epoch: Number(next.transcript_epoch ?? 0),
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
    used_language: next.used_language ?? null,
    used_summary_language: next.used_summary_language ?? null,
    used_whisper_model: next.used_whisper_model ?? null,
    used_summary_model: next.used_summary_model ?? null,
    used_summary_preset: next.used_summary_preset ?? null,
    used_summary_length: next.used_summary_length ?? null,
    used_has_extra_instructions: Boolean(next.used_has_extra_instructions),
  };
}

function labelFromOptions(
  id: string | null | undefined,
  options: { id: string; label: string }[],
): string | null {
  if (!id) return null;
  return options.find((o) => o.id === id)?.label ?? id;
}

function localizePresets(
  items: SummaryPresetOption[],
): SummaryPresetOption[] {
  return items.map((item) => ({
    ...item,
    label: t(`presets.${item.id}`, undefined, item.label),
  }));
}

function localizeWhisperModels(items: ModelOption[]): ModelOption[] {
  return items.map((item) => ({
    ...item,
    label: t(`models.whisper.${item.id}.label`, undefined, item.label),
    hint: item.hint
      ? t(`models.whisper.${item.id}.hint`, undefined, item.hint)
      : item.hint,
  }));
}

function localizeSummaryModels(items: ModelOption[]): ModelOption[] {
  return items.map((item) => ({
    ...item,
    label: t(`models.summary.${item.id}.label`, undefined, item.label),
    hint: item.hint
      ? t(`models.summary.${item.id}.hint`, undefined, item.hint)
      : item.hint,
  }));
}

function fallbackPresets(): SummaryPresetOption[] {
  return FALLBACK_PRESET_IDS.map((id) => ({
    id,
    label: t(`presets.${id}`),
  }));
}

function fallbackWhisper(): ModelOption[] {
  return FALLBACK_WHISPER_IDS.map((id) => ({
    id,
    label: t(`models.whisper.${id}.label`),
    hint: t(`models.whisper.${id}.hint`),
  }));
}

function fallbackSummaryModels(): ModelOption[] {
  return FALLBACK_SUMMARY_IDS.map((id) => ({
    id,
    label: t(`models.summary.${id}.label`),
    hint: t(`models.summary.${id}.hint`),
  }));
}

function buildUsedMetaTags(
  state: AppState,
  whisperModels: ModelOption[],
  summaryModels: ModelOption[],
  presets: SummaryPresetOption[],
): { key: string; label: string }[] {
  const tags: { key: string; label: string }[] = [];
  if (state.used_language) {
    tags.push({
      key: "lang",
      label: t("meta.transcriptLanguage", {
        name: languageLabel(state.used_language),
      }),
    });
  }
  if (
    state.used_summary_language &&
    state.used_summary_language !== state.used_language
  ) {
    tags.push({
      key: "summary-lang",
      label: t("meta.summaryLanguage", {
        name: languageLabel(state.used_summary_language),
      }),
    });
  } else if (state.used_summary_language && !state.used_language) {
    tags.push({
      key: "summary-lang",
      label: t("meta.summaryLanguage", {
        name: languageLabel(state.used_summary_language),
      }),
    });
  }
  const whisper = labelFromOptions(state.used_whisper_model, whisperModels);
  if (whisper) {
    tags.push({ key: "whisper", label: t("meta.whisper", { name: whisper }) });
  }
  const summaryModel = labelFromOptions(state.used_summary_model, summaryModels);
  if (summaryModel) {
    tags.push({
      key: "summary-model",
      label: t("meta.notes", { name: summaryModel }),
    });
  }
  const preset = labelFromOptions(state.used_summary_preset, presets);
  if (preset) {
    tags.push({ key: "preset", label: preset });
  }
  if (state.used_summary_length) {
    tags.push({
      key: "length",
      label: t(`length.${state.used_summary_length}`, undefined, state.used_summary_length),
    });
  }
  if (state.used_has_extra_instructions) {
    tags.push({ key: "extra", label: t("meta.customInstructions") });
  }
  return tags;
}

function statusLabel(
  status: AppState["status"],
  summaryStatus: SummaryStatus,
): string {
  if (status === "completed" && isSummaryBusy(summaryStatus)) {
    return summaryStatus === "loading_model"
      ? t("status.loadingSummaryModel")
      : t("status.summarizing");
  }
  switch (status) {
    case "idle":
      return t("status.idle");
    case "ready":
      return t("status.ready");
    case "recording":
      return t("status.recording");
    case "loading_model":
      return t("status.loadingModel");
    case "transcribing":
      return t("status.transcribing");
    case "completed":
      return t("status.completed");
    case "error":
      return t("status.error");
    default:
      return status;
  }
}


export default function App() {
  const { locale, localePreference, setLocalePreference } = useI18n();
  const { themePreference, setThemePreference } = useTheme();
  const [state, setState] = useState<AppState>(getDefaultState);
  const [bridgeError, setBridgeError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const [exported, setExported] = useState(false);
  const [resultTab, setResultTab] = useState<ResultTab>("transcript");
  const [presetsRaw, setPresetsRaw] = useState<SummaryPresetOption[]>(() =>
    fallbackPresets(),
  );
  const [whisperModelsRaw, setWhisperModelsRaw] = useState<ModelOption[]>(() =>
    fallbackWhisper(),
  );
  const [summaryModelsRaw, setSummaryModelsRaw] = useState<ModelOption[]>(() =>
    fallbackSummaryModels(),
  );
  const [instructionsDraft, setInstructionsDraft] = useState("");
  const [transcriptDraft, setTranscriptDraft] = useState("");
  const [summaryStale, setSummaryStale] = useState(false);
  const [summaryOptionsOpen, setSummaryOptionsOpen] = useState(false);
  const [sidebarSettingsOpen, setSidebarSettingsOpen] = useState(false);
  const [appVersion, setAppVersion] = useState<string | null>(null);
  const [sessions, setSessions] = useState<HistorySession[]>([]);
  const [playback, setPlayback] = useState<PlaybackState>("idle");
  const copyTimer = useRef<number | null>(null);
  const exportTimer = useRef<number | null>(null);
  const instructionsTimer = useRef<number | null>(null);
  const transcriptPersistTimer = useRef<number | null>(null);
  const transcriptDirtyRef = useRef(false);
  const transcriptDraftRef = useRef("");
  const transcriptFlushEpochRef = useRef(0);
  const transcriptEpochRef = useRef(0);
  const summaryRunActiveRef = useRef(false);
  const summarizedFromRef = useRef("");
  const lastTranscriptRef = useRef("");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const audioPathRef = useRef<string | null>(null);

  // Recompute catalog labels whenever the active locale changes.
  void locale;
  const presets = localizePresets(presetsRaw);
  const whisperModels = localizeWhisperModels(whisperModelsRaw);
  const summaryModels = localizeSummaryModels(summaryModelsRaw);

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
            ? api.get_summary_presets().catch(() => fallbackPresets())
            : Promise.resolve(fallbackPresets()),
          api.get_whisper_models
            ? api.get_whisper_models().catch(() => fallbackWhisper())
            : Promise.resolve(fallbackWhisper()),
          api.get_summary_models
            ? api.get_summary_models().catch(() => fallbackSummaryModels())
            : Promise.resolve(fallbackSummaryModels()),
        ]);
        if (cancelled) return;
        const merged = mergeState(initial);
        setState(merged);
        setTranscriptDraft(merged.transcript || "");
        transcriptDraftRef.current = merged.transcript || "";
        transcriptEpochRef.current = Number(merged.transcript_epoch ?? 0);
        transcriptDirtyRef.current = false;
        setSummaryStale(false);
        summaryRunActiveRef.current = false;
        summarizedFromRef.current = "";
        setInstructionsDraft(merged.additional_instructions);
        if (!merged.summary_language_persisted && api.update_settings) {
          const seeded = summaryLanguageFromUiLocale(getLocale());
          try {
            const seededState = await api.update_settings({
              summary_language: seeded,
            });
            if (!cancelled && seededState) {
              setState(mergeState(seededState));
            }
          } catch {
            // Seed is best-effort; interim DEFAULT_LANGUAGE remains usable.
          }
        }
        if (Array.isArray(presetList) && presetList.length > 0) {
          setPresetsRaw(presetList);
        }
        if (Array.isArray(whisperList) && whisperList.length > 0) {
          setWhisperModelsRaw(whisperList);
        }
        if (Array.isArray(summaryList) && summaryList.length > 0) {
          setSummaryModelsRaw(summaryList);
        }
        if (api.list_sessions) {
          try {
            const items = await api.list_sessions();
            if (!cancelled && Array.isArray(items)) setSessions(items);
          } catch {
            // History optional on older bridges.
          }
        }
        if (api.get_app_info) {
          try {
            const info = await api.get_app_info();
            const ver = (info?.version || "").trim();
            if (!cancelled && ver) setAppVersion(ver);
          } catch {
            // Version is optional chrome.
          }
        }
        setBridgeError(null);

        intervalId = window.setInterval(async () => {
          try {
            const next = await api.get_state();
            if (cancelled) return;
            const merged = mergeState(next);
            transcriptEpochRef.current = Number(merged.transcript_epoch ?? 0);
            if (transcriptDirtyRef.current) {
              merged.transcript = transcriptDraftRef.current;
            }
            setState(merged);
          } catch {
            // Keep last known state if a poll fails briefly.
          }
        }, 400);
      } catch (err) {
        if (!cancelled) {
          setBridgeError(
            err instanceof Error ? err.message : t("errors.bridgeUnavailable"),
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
      if (transcriptPersistTimer.current) {
        window.clearTimeout(transcriptPersistTimer.current);
      }
      teardownAudio();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function teardownAudio() {
    const el = audioRef.current;
    if (el) {
      el.pause();
      el.removeAttribute("src");
      el.load();
    }
    audioRef.current = null;
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
    audioPathRef.current = null;
    setPlayback("idle");
  }

  useEffect(() => {
    // Drop loaded audio when the source file changes or clears.
    if (audioPathRef.current && audioPathRef.current !== state.file_path) {
      teardownAudio();
    }
    if (!state.file_path && audioRef.current) {
      teardownAudio();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.file_path]);

  async function retryBridge() {
    resetApi();
    window.location.reload();
  }

  useEffect(() => {
    // Accept bridge transcript when not dirty, or when Transcribe/clear replaces it.
    const pipelineReplace =
      state.status === "loading_model" ||
      state.status === "transcribing" ||
      (!state.transcript && Boolean(lastTranscriptRef.current));
    if (pipelineReplace) {
      transcriptFlushEpochRef.current += 1;
      transcriptDirtyRef.current = false;
      setTranscriptDraft(state.transcript || "");
      transcriptDraftRef.current = state.transcript || "";
      transcriptEpochRef.current = Number(state.transcript_epoch ?? 0);
      setSummaryStale(false);
      summaryRunActiveRef.current = false;
      summarizedFromRef.current = "";
    } else if (!transcriptDirtyRef.current && state.transcript !== transcriptDraftRef.current) {
      setTranscriptDraft(state.transcript || "");
      transcriptDraftRef.current = state.transcript || "";
      transcriptEpochRef.current = Number(state.transcript_epoch ?? 0);
    } else {
      transcriptEpochRef.current = Number(state.transcript_epoch ?? 0);
    }
    if (state.transcript && state.transcript !== lastTranscriptRef.current) {
      setResultTab("transcript");
    }
    lastTranscriptRef.current = state.transcript;
  }, [state.transcript, state.status, state.transcript_epoch]);

  useEffect(() => {
    const busySummary =
      state.summary_status === "loading_model" ||
      state.summary_status === "summarizing";
    if (busySummary) {
      if (!summaryRunActiveRef.current) {
        summaryRunActiveRef.current = true;
        summarizedFromRef.current = transcriptDraftRef.current;
      }
      return;
    }
    if (summaryRunActiveRef.current) {
      summaryRunActiveRef.current = false;
      if (state.summary_status === "completed" && state.summary?.trim()) {
        setSummaryStale(transcriptDraftRef.current !== summarizedFromRef.current);
      }
    }
  }, [state.summary_status, state.summary]);

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
      transcriptEpochRef.current = Number(merged.transcript_epoch ?? 0);
      if (transcriptDirtyRef.current) {
        merged.transcript = transcriptDraftRef.current;
      } else {
        setTranscriptDraft(merged.transcript || "");
        transcriptDraftRef.current = merged.transcript || "";
      }
      setState(merged);
      setBridgeError(null);
      return merged;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : t("errors.bridgeUnavailable");
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
  const usedMetaTags = buildUsedMetaTags(state, whisperModels, summaryModels, presets);
  const locked = busy || recording;
  const canTranscribe = Boolean(state.file_path) && !locked;
  const language = state.language || DEFAULT_LANGUAGE;
  const summaryLanguage =
    state.summary_language || state.language || DEFAULT_LANGUAGE;
  const displayTranscript = transcriptDraft;
  const hasTranscript = Boolean(displayTranscript?.trim());
  const audioLocked =
    Boolean(state.session_id) ||
    Boolean(state.transcript?.trim()) ||
    hasTranscript;
  const activeText =
    resultTab === "summary" ? state.summary : displayTranscript;
  const canCopy = Boolean(activeText);
  const canExport = Boolean(displayTranscript?.trim() || state.summary?.trim());
  const summaryLength = (state.summary_length || "normal") as SummaryLength;
  const showRegenHint = summaryStale && Boolean(state.summary?.trim());

  async function flushTranscript(): Promise<boolean> {
    if (!transcriptDirtyRef.current) return true;
    if (transcriptPersistTimer.current) {
      window.clearTimeout(transcriptPersistTimer.current);
      transcriptPersistTimer.current = null;
    }
    const flushEpoch = transcriptFlushEpochRef.current;
    const basedOnEpoch = transcriptEpochRef.current;
    const text = transcriptDraftRef.current;
    try {
      const api = await getApi();
      if (flushEpoch !== transcriptFlushEpochRef.current) {
        return false;
      }
      if (!transcriptDirtyRef.current) {
        return true;
      }
      if (!api.update_transcript) {
        setBridgeError(t("errors.bridgeUnavailable"));
        return false;
      }
      const next = await api.update_transcript(text, basedOnEpoch);
      if (flushEpoch !== transcriptFlushEpochRef.current) {
        return false;
      }
      if (next.ok === false) {
        setBridgeError(next.error || t("errors.bridgeUnavailable"));
        return false;
      }
      const merged = mergeState(next);
      transcriptDirtyRef.current = false;
      const saved = merged.transcript || text;
      setTranscriptDraft(saved);
      transcriptDraftRef.current = saved;
      transcriptEpochRef.current = Number(merged.transcript_epoch ?? basedOnEpoch + 1);
      setState(merged);
      setBridgeError(null);
      return true;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : t("errors.bridgeUnavailable");
      if (message.includes("Desktop bridge is not available")) {
        resetApi();
      }
      setBridgeError(message);
      return false;
    }
  }

  function onTranscriptChange(value: string) {
    transcriptDirtyRef.current = true;
    setTranscriptDraft(value);
    transcriptDraftRef.current = value;
    setState((prev) => ({ ...prev, transcript: value }));
    const summaryPresent = Boolean(state.summary?.trim());
    const summarizingNow =
      state.summary_status === "loading_model" ||
      state.summary_status === "summarizing";
    if (summaryPresent || summarizingNow) {
      setSummaryStale(value !== summarizedFromRef.current);
    }
    if (transcriptPersistTimer.current) {
      window.clearTimeout(transcriptPersistTimer.current);
    }
    transcriptPersistTimer.current = window.setTimeout(() => {
      void flushTranscript();
    }, 450);
  }

  function clearTranscriptDraft() {
    transcriptFlushEpochRef.current += 1;
    transcriptDirtyRef.current = false;
    setTranscriptDraft("");
    transcriptDraftRef.current = "";
    setSummaryStale(false);
    summaryRunActiveRef.current = false;
    summarizedFromRef.current = "";
    if (transcriptPersistTimer.current) {
      window.clearTimeout(transcriptPersistTimer.current);
      transcriptPersistTimer.current = null;
    }
  }

  async function onSelectFile() {
    await withApi((api) => api.select_file());
  }

  async function onSaveAudioCopy() {
    await withApi((api) => api.save_audio_copy());
  }

  async function ensurePlaybackAudio(): Promise<HTMLAudioElement | null> {
    const path = state.file_path;
    if (!path) return null;
    if (audioRef.current && audioPathRef.current === path) {
      return audioRef.current;
    }

    teardownAudio();
    try {
      const api = await getApi();
      if (!api.get_playback_src) {
        setBridgeError(t("errors.playbackUnavailable"));
        return null;
      }
      const result = await api.get_playback_src();
      if (!result.ok || !result.data_base64 || !result.mime) {
        setBridgeError(result.error || t("errors.playbackPrepare"));
        return null;
      }
      const binary = atob(result.data_base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) {
        bytes[i] = binary.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: result.mime });
      const url = URL.createObjectURL(blob);
      const el = new Audio(url);
      el.addEventListener("ended", () => setPlayback("idle"));
      el.addEventListener("error", () => {
        setBridgeError(t("errors.playbackPlay"));
        setPlayback("idle");
      });
      audioRef.current = el;
      audioUrlRef.current = url;
      audioPathRef.current = path;
      setBridgeError(null);
      return el;
    } catch (err) {
      const message =
        err instanceof Error ? err.message : t("errors.bridgeUnavailable");
      setBridgeError(message);
      return null;
    }
  }

  async function onPlayAudio() {
    const el = await ensurePlaybackAudio();
    if (!el) return;
    try {
      await el.play();
      setPlayback("playing");
    } catch {
      setBridgeError(t("errors.playbackStart"));
      setPlayback("idle");
    }
  }

  function onPauseAudio() {
    const el = audioRef.current;
    if (!el) return;
    el.pause();
    setPlayback("paused");
  }

  function onStopAudio() {
    const el = audioRef.current;
    if (!el) {
      setPlayback("idle");
      return;
    }
    el.pause();
    el.currentTime = 0;
    setPlayback("idle");
  }

  function renderPlaybackControls() {
    if (!state.file_path || recording) return null;
    if (playback === "playing") {
      return (
        <>
          <button
            type="button"
            className="btn secondary icon-btn"
            onClick={onPauseAudio}
            title={t("common.pause")}
            aria-label={t("common.pause")}
          >
            <IconPause />
          </button>
          <button
            type="button"
            className="btn secondary icon-btn"
            onClick={onStopAudio}
            title={t("common.stop")}
            aria-label={t("common.stop")}
          >
            <IconStop />
          </button>
        </>
      );
    }
    if (playback === "paused") {
      return (
        <>
          <button
            type="button"
            className="btn secondary icon-btn"
            onClick={() => void onPlayAudio()}
            title={t("common.play")}
            aria-label={t("common.play")}
          >
            <IconPlay />
          </button>
          <button
            type="button"
            className="btn secondary icon-btn"
            onClick={onStopAudio}
            title={t("common.stop")}
            aria-label={t("common.stop")}
          >
            <IconStop />
          </button>
        </>
      );
    }
    return (
      <button
        type="button"
        className="btn secondary icon-btn"
        onClick={() => void onPlayAudio()}
        title={t("common.play")}
        aria-label={t("common.play")}
      >
        <IconPlay />
      </button>
    );
  }

  async function onExportNotes() {
    const flushed = await flushTranscript();
    if (!flushed) return;
    try {
      const api = await getApi();
      if (!api.export_notes) {
        setBridgeError(t("errors.exportUnavailable"));
        return;
      }
      const next = await api.export_notes();
      const merged = mergeState(next);
      if (transcriptDirtyRef.current) {
        merged.transcript = transcriptDraftRef.current;
      }
      setState(merged);
      setBridgeError(null);
      if (next.ok) {
        setExported(true);
        if (exportTimer.current) window.clearTimeout(exportTimer.current);
        exportTimer.current = window.setTimeout(() => setExported(false), 1600);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : t("errors.bridgeUnavailable");
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
      language: string;
      summary_language: string;
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
    clearTranscriptDraft();
    const merged = await withApi((api) => api.open_session(sessionId));
    if (merged?.summary?.trim()) {
      summarizedFromRef.current = merged.transcript || "";
      setSummaryStale(false);
    }
    setResultTab("transcript");
  }

  async function onNewTranscript() {
    if (!state.session_id && !state.file_path && !state.transcript) {
      setResultTab("transcript");
      return;
    }
    teardownAudio();
    clearTranscriptDraft();
    await withApi((api) => api.reset_for_another_file());
    setResultTab("transcript");
  }

  async function onDeleteSession(sessionId: string) {
    const label =
      sessions.find((s) => s.id === sessionId)?.title ||
      t("history.sessionFallback");
    if (!window.confirm(t("history.deleteConfirm", { title: label }))) return;
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
    clearTranscriptDraft();
    await withApi((api) => api.start_transcription());
  }

  async function onCancel() {
    await withApi((api) => api.cancel_transcription());
  }

  async function onRecord() {
    teardownAudio();
    await withApi((api) => api.start_recording());
  }

  async function onStopRecord() {
    await withApi((api) => api.stop_recording());
  }

  async function onSummarize() {
    const flushed = await flushTranscript();
    if (!flushed) return;
    summarizedFromRef.current = transcriptDraftRef.current;
    summaryRunActiveRef.current = true;
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
  const pageTitle = (state.session_title || "").trim() || t("history.newTranscript");
  const isNewTranscript = !state.session_id;

  return (
    <div className="shell">
      <aside className="history-sidebar" aria-label={t("history.aria")}>
        <div className="history-sidebar-inner">
          <button
            type="button"
            className={`history-new ${isNewTranscript ? "active" : ""}`}
            disabled={locked || summaryBusy}
            onClick={() => void onNewTranscript()}
          >
            <IconPlus className="history-new-icon" />
            {t("history.newTranscript")}
          </button>
          <div className="history-list">
            {sessions.length === 0 ? (
              <p className="history-empty">{t("history.empty")}</p>
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
                        {session.title || t("history.newTranscript")}
                      </span>
                    </button>
                    <button
                      type="button"
                      className="history-item-delete"
                      disabled={locked || summaryBusy}
                      aria-label={t("history.deleteAria", { title: session.title || t("history.session") })}
                      onClick={() => void onDeleteSession(session.id)}
                    >
                      ×
                    </button>
                  </div>
                );
              })
            )}
          </div>
          <div
            className={`history-sidebar-footer ${sidebarSettingsOpen ? "open" : ""}`}
          >
            {sidebarSettingsOpen && (
              <div
                id="sidebar-settings-panel"
                className="sidebar-settings-panel"
                role="region"
                aria-label={t("sidebar.settingsAria")}
              >
                <div className="sidebar-setting">
                  <span className="sidebar-setting-label" id="sidebar-ui-language">
                    {t("sidebar.uiLanguage")}
                  </span>
                  <div
                    className="segmented sidebar-locale"
                    role="group"
                    aria-labelledby="sidebar-ui-language"
                  >
                    {LOCALE_OPTIONS.map((option) => {
                      const short = option.shortKey
                        ? t(option.shortKey)
                        : option.short || option.id;
                      const label = option.labelKey
                        ? t(option.labelKey)
                        : option.label || option.id;
                      return (
                        <button
                          key={option.id}
                          type="button"
                          className={localePreference === option.id ? "active" : ""}
                          aria-pressed={localePreference === option.id}
                          title={label}
                          onClick={() => setLocalePreference(option.id)}
                        >
                          {short}
                        </button>
                      );
                    })}
                  </div>
                </div>
                <div className="sidebar-setting">
                  <span className="sidebar-setting-label" id="sidebar-ui-theme">
                    {t("sidebar.theme")}
                  </span>
                  <div
                    className="segmented sidebar-theme"
                    role="group"
                    aria-labelledby="sidebar-ui-theme"
                  >
                    <button
                      type="button"
                      className={themePreference === "system" ? "active" : ""}
                      aria-pressed={themePreference === "system"}
                      title={t("sidebar.themeSystem")}
                      aria-label={t("sidebar.themeSystem")}
                      onClick={() => setThemePreference("system")}
                    >
                      <IconMonitor />
                    </button>
                    <button
                      type="button"
                      className={themePreference === "light" ? "active" : ""}
                      aria-pressed={themePreference === "light"}
                      title={t("sidebar.themeLight")}
                      aria-label={t("sidebar.themeLight")}
                      onClick={() => setThemePreference("light")}
                    >
                      <IconSun />
                    </button>
                    <button
                      type="button"
                      className={themePreference === "dark" ? "active" : ""}
                      aria-pressed={themePreference === "dark"}
                      title={t("sidebar.themeDark")}
                      aria-label={t("sidebar.themeDark")}
                      onClick={() => setThemePreference("dark")}
                    >
                      <IconMoon />
                    </button>
                  </div>
                </div>
              </div>
            )}
            <button
              type="button"
              className="sidebar-settings-toggle"
              aria-expanded={sidebarSettingsOpen}
              aria-controls="sidebar-settings-panel"
              onClick={() => setSidebarSettingsOpen((open) => !open)}
            >
              <span>{t("sidebar.settings")}</span>
              <span className="sidebar-settings-chevron" aria-hidden="true" />
            </button>
          </div>
        </div>
        {appVersion && (
          <p className="sidebar-version" title={t("sidebar.version", { version: appVersion })}>
            v{appVersion}
          </p>
        )}
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
                {t("common.retry")}
              </button>
            )}
          </div>
        </div>
      )}

      <section className="panel">
        <h2>{t("file.title")}</h2>
        {recording ? (
          <div className="record-active" aria-live="polite">
            <div className="record-active-meta">
              <span className="record-pulse" aria-hidden="true" />
              <div>
                <p className="record-active-title">{t("file.recording")}</p>
                <p className="record-active-hint">{t("file.recordingHint")}</p>
              </div>
            </div>
            <p className="record-timer">{formatElapsed(state.elapsed_seconds)}</p>
            <button
              type="button"
              className="btn stop-record"
              onClick={() => void onStopRecord()}
              aria-label={t("file.stopRecording")}
            >
              <span className="stop-square" aria-hidden="true" />
              {t("common.stop")}
            </button>
          </div>
        ) : audioLocked ? (
          <div className="file-locked" aria-label={t("file.sourceAudio")}>
            {state.file_path ? (
              <div className="file-locked-actions">
                {renderPlaybackControls()}
                <button
                  type="button"
                  className="btn secondary icon-btn"
                  onClick={() => void onSaveAudioCopy()}
                  disabled={locked}
                  title={t("file.saveCopy")}
                  aria-label={t("file.saveCopy")}
                >
                  <IconSave />
                </button>
              </div>
            ) : (
              <p className="file-locked-empty">{t("file.noAudio")}</p>
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
              {state.file_name ? state.file_name : t("file.dropHere")}
            </p>
            <p className="drop-hint">
              {t("file.supported", { formats: ACCEPTED.replaceAll(",", " ") })}
            </p>
            <div className="drop-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => void onSelectFile()}
                disabled={locked}
              >
                {t("file.selectFile")}
              </button>
              {renderPlaybackControls()}
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
                aria-label={t("file.recordAria")}
              >
                <span className="record-dot" aria-hidden="true" />
                {t("file.record")}
              </button>
            </div>
          </div>
        )}
      </section>

      <section className="panel row language-row">
        <div className="field">
          <h2>{t("language.transcriptTitle")}</h2>
          <label className="sr-only" htmlFor="transcript-language-select">
            {t("language.transcriptTitle")}
          </label>
          <LanguageSelect
            value={language}
            inputId="transcript-language-select"
            listAriaLabel={t("language.transcriptListAria")}
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
            {t("actions.transcribe")}
          </button>
          {busy && (
            <button
              type="button"
              className="btn ghost"
              onClick={() => void onCancel()}
            >
              {t("common.cancel")}
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
            <span className="disclosure-title">{t("processing.title")}</span>
            <span className="disclosure-hint">
              {t("processing.hint")}
            </span>
          </span>
          <span className="disclosure-chevron" aria-hidden="true" />
        </button>

        {summaryOptionsOpen && (
          <div id="summary-options-body" className="summary-settings-body">
            {state.hardware_reason && (
              <p className="hardware-hint">
                {t("processing.recommended", {
                  tier: state.performance_tier || t("processing.tierAuto"),
                  reason: state.hardware_reason,
                })}
              </p>
            )}

            <div className="field">
              <label className="field-label" htmlFor="summary-language-select">
                {t("language.summaryTitle")}
              </label>
              <LanguageSelect
                value={summaryLanguage}
                inputId="summary-language-select"
                listAriaLabel={t("language.summaryListAria")}
                disabled={locked || summaryBusy}
                onChange={(next) =>
                  void onSettingsPatch({ summary_language: next })
                }
              />
            </div>

            <div className="summary-settings-grid">
              <div className="field">
                <label className="field-label" htmlFor="whisper-model">
                  {t("processing.transcriptionModel")}
                </label>
                <PresetSelect
                  value={state.whisper_model || "medium"}
                  options={whisperModels}
                  inputId="whisper-model"
                  ariaLabel={t("processing.transcriptionModelsAria")}
                  searchPlaceholder={t("processing.searchModel")}
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ whisper_model: next })}
                />
              </div>

              <div className="field">
                <label className="field-label" htmlFor="summary-model">
                  {t("processing.summaryModel")}
                </label>
                <PresetSelect
                  value={state.summary_model || "3b"}
                  options={summaryModels}
                  inputId="summary-model"
                  ariaLabel={t("processing.summaryModelsAria")}
                  searchPlaceholder={t("processing.searchModel")}
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ summary_model: next })}
                />
              </div>
            </div>

            <div className="summary-settings-grid">
              <div className="field">
                <label className="field-label" htmlFor="summary-preset">
                  {t("processing.preset")}
                </label>
                <PresetSelect
                  value={state.summary_preset || "meeting_notes"}
                  options={presets}
                  inputId="summary-preset"
                  ariaLabel={t("processing.presetsAria")}
                  searchPlaceholder={t("processing.searchPreset")}
                  disabled={locked || summaryBusy}
                  onChange={(next) => void onSettingsPatch({ summary_preset: next })}
                />
              </div>

              <div className="field">
                <span className="field-label" id="summary-length-label">
                  {t("processing.length")}
                </span>
                <div
                  className="segmented"
                  role="group"
                  aria-labelledby="summary-length-label"
                >
                  {LENGTH_IDS.map((id) => (
                    <button
                      key={id}
                      type="button"
                      className={summaryLength === id ? "active" : ""}
                      disabled={locked || summaryBusy}
                      aria-pressed={summaryLength === id}
                      onClick={() => void onSettingsPatch({ summary_length: id })}
                    >
                      {t(`length.${id}`)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="field instructions-field">
              <label className="field-label" htmlFor="summary-instructions">
                {t("processing.additionalInstructions")}
              </label>
              <textarea
                id="summary-instructions"
                className="instructions-input"
                rows={2}
                maxLength={800}
                placeholder={t("processing.instructionsPlaceholder")}
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
              <span>{t("processing.autoSummary")}</span>
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
        {usedMetaTags.length > 0 && (
          <ul className="meta-tags" aria-label={t("status.usedSettingsAria")}>
            {usedMetaTags.map((tag) => (
              <li key={tag.key} className="meta-tag">
                {tag.label}
              </li>
            ))}
          </ul>
        )}
        {(busy || recording || summaryBusy) && (
          <div
            className="progress indeterminate"
            role="progressbar"
            aria-valuetext={
              recording
                ? t("status.recording")
                : summaryBusy
                  ? t("status.summarizing")
                  : t("status.processing")
            }
          >
            <div className="bar" />
          </div>
        )}
      </section>

      {showResult && (
        <section className="panel result-panel">
          <div className="result-header">
            <div className="result-tabs" role="tablist" aria-label={t("result.aria")}>
              <button
                type="button"
                role="tab"
                aria-selected={resultTab === "transcript"}
                className={`result-tab ${resultTab === "transcript" ? "active" : ""}`}
                onClick={() => setResultTab("transcript")}
              >
                {t("result.transcript")}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={resultTab === "summary"}
                className={`result-tab ${resultTab === "summary" ? "active" : ""}`}
                onClick={() => setResultTab("summary")}
              >
                {t("result.summary")}
              </button>
            </div>
            <div className="result-actions">
              {resultTab === "summary" && summaryBusy && (
                <button
                  type="button"
                  className="btn ghost"
                  onClick={() => void onCancelSummary()}
                >
                  {t("common.cancel")}
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
                    title={t("result.generateSummary")}
                    aria-label={t("result.generateSummary")}
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
                    title={t("result.regenerateSummary")}
                    aria-label={t("result.regenerateSummary")}
                  >
                    <IconRefresh />
                  </button>
                )}
              <button
                type="button"
                className="btn ghost icon-btn"
                onClick={() => void onExportNotes()}
                disabled={!canExport}
                title={exported ? t("common.exported") : t("common.export")}
                aria-label={exported ? t("common.exported") : t("result.exportNotes")}
              >
                {exported ? <IconCheck /> : <IconExport />}
              </button>
              <button
                type="button"
                className="btn secondary icon-btn"
                onClick={() => void onCopy()}
                disabled={!canCopy}
                title={copied ? t("common.copied") : t("common.copy")}
                aria-label={copied ? t("common.copied") : t("common.copy")}
              >
                {copied ? <IconCheck /> : <IconCopy />}
              </button>
            </div>
          </div>

          {resultTab === "transcript" ? (
            <div className="transcript-edit">
              <textarea
                id="transcript-editor"
                className="transcript-editor"
                value={transcriptDraft}
                onChange={(e) => onTranscriptChange(e.target.value)}
                disabled={locked}
                spellCheck
                aria-label={t("result.transcript")}
                placeholder={t("result.transcriptEmpty")}
              />
              {showRegenHint && (
                <p className="transcript-edit-hint">{t("result.transcriptEditedHint")}</p>
              )}
            </div>
          ) : summaryBusy ? (
            <div className="summary-empty" aria-live="polite">
              <div className="summary-busy">
                <span className="spinner" aria-hidden="true" />
                <p>
                  {state.summary_status === "loading_model"
                    ? t("result.loadingSummaryModel")
                    : t("result.writingSummary")}
                </p>
              </div>
            </div>
          ) : state.summary ? (
            <MarkdownBody
              content={state.summary}
              emptyLabel={t("result.summaryEmpty")}
            />
          ) : (
            <div className="summary-empty">
              <p>
                {state.summary_status === "error"
                  ? t("result.summaryFailed")
                  : state.auto_summary
                    ? t("result.summaryAfterTranscription")
                    : t("result.autoSummaryOff")}
              </p>
              {Boolean(state.transcript) && (
                <button
                  type="button"
                  className="btn secondary icon-btn"
                  onClick={() => void onSummarize()}
                  title={t("result.generateSummary")}
                  aria-label={t("result.generateSummary")}
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
