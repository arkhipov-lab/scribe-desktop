import { useSyncExternalStore } from "react";

export type ThemeId = "light" | "dark";
export type ThemePreference = "system" | ThemeId;

const STORAGE_KEY = "scribe.theme";
const PREFERENCES: ThemePreference[] = ["system", "light", "dark"];

const listeners = new Set<() => void>();
let themePreference = readPreference();
let currentTheme = resolveTheme(themePreference);

function notify(): void {
  listeners.forEach((fn) => fn());
}

function readPreference(): ThemePreference {
  try {
    const stored = window.localStorage?.getItem(STORAGE_KEY);
    if (stored === "system" || stored === "light" || stored === "dark") {
      return stored;
    }
  } catch {
    // ignore
  }
  return "system";
}

function systemTheme(): ThemeId {
  if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

function resolveTheme(preference: ThemePreference): ThemeId {
  if (preference === "light" || preference === "dark") return preference;
  return systemTheme();
}

function persistPreference(preference: ThemePreference): void {
  try {
    window.localStorage?.setItem(STORAGE_KEY, preference);
  } catch {
    // ignore
  }
}

function syncFromSystem(): void {
  if (themePreference !== "system") return;
  const next = resolveTheme("system");
  if (next === currentTheme) return;
  currentTheme = next;
  applyTheme(next);
  notify();
}

function mediaQuery(): MediaQueryList | null {
  return window.matchMedia?.("(prefers-color-scheme: dark)") ?? null;
}

function ensureSystemListener(): void {
  const mq = mediaQuery();
  if (!mq) return;
  // Safari < 14 uses addListener.
  if (typeof mq.addEventListener === "function") {
    mq.addEventListener("change", syncFromSystem);
  } else if (typeof mq.addListener === "function") {
    mq.addListener(syncFromSystem);
  }
}

ensureSystemListener();

export function getTheme(): ThemeId {
  return currentTheme;
}

export function getThemePreference(): ThemePreference {
  return themePreference;
}

export function applyTheme(theme: ThemeId): void {
  document.documentElement.dataset.theme = theme;
}

export function setThemePreference(preference: ThemePreference): void {
  const nextPref = PREFERENCES.includes(preference) ? preference : "system";
  const nextTheme = resolveTheme(nextPref);
  const changed = nextPref !== themePreference || nextTheme !== currentTheme;
  themePreference = nextPref;
  currentTheme = nextTheme;
  applyTheme(nextTheme);
  persistPreference(nextPref);
  if (changed) notify();
}

/** Convenience alias used by the UI. */
export function setTheme(preference: ThemePreference): void {
  setThemePreference(preference);
}

export function subscribeTheme(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/** Apply stored/system theme before first paint. */
export function initTheme(): ThemeId {
  applyTheme(currentTheme);
  return currentTheme;
}

export function useTheme(): {
  theme: ThemeId;
  themePreference: ThemePreference;
  setTheme: typeof setThemePreference;
  setThemePreference: typeof setThemePreference;
} {
  const theme = useSyncExternalStore(
    subscribeTheme,
    getTheme,
    (): ThemeId => "light",
  );
  const themePreferenceValue = useSyncExternalStore(
    subscribeTheme,
    getThemePreference,
    (): ThemePreference => "system",
  );
  return {
    theme,
    themePreference: themePreferenceValue,
    setTheme: setThemePreference,
    setThemePreference,
  };
}
