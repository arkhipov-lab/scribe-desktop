import { useSyncExternalStore } from "react";
import en from "./locales/en.json";
import ru from "./locales/ru.json";

export type LocaleMessages = typeof en;
export type TranslateVars = Record<string, string | number>;
export type LocalePreference = "system" | "en" | "ru";

const STORAGE_KEY = "scribe.locale";
const CATALOGS: Record<string, LocaleMessages> = {
  en,
  ru,
};

const listeners = new Set<() => void>();
let localePreference = readPreference();
let currentLocale = resolveLocale(localePreference);

function notify(): void {
  listeners.forEach((fn) => fn());
}

function readPreference(): LocalePreference {
  try {
    const stored = window.localStorage?.getItem(STORAGE_KEY);
    if (stored === "system" || stored === "en" || stored === "ru") return stored;
    // Legacy: explicit locale without "system" key.
    if (stored && CATALOGS[stored]) return stored as LocalePreference;
  } catch {
    // ignore
  }
  return "system";
}

function systemLocale(): string {
  const nav = (navigator.language || "en").toLowerCase();
  const short = nav.split("-")[0] || "en";
  return CATALOGS[short] ? short : "en";
}

function resolveLocale(preference: LocalePreference): string {
  if (preference === "system") return systemLocale();
  return CATALOGS[preference] ? preference : "en";
}

function persistPreference(preference: LocalePreference): void {
  try {
    window.localStorage?.setItem(STORAGE_KEY, preference);
  } catch {
    // ignore
  }
}

function syncFromSystem(): void {
  if (localePreference !== "system") return;
  const next = resolveLocale("system");
  if (next === currentLocale) return;
  currentLocale = next;
  notify();
}

function ensureSystemListener(): void {
  window.addEventListener("languagechange", syncFromSystem);
}

ensureSystemListener();

export function getLocale(): string {
  return currentLocale;
}

export function getLocalePreference(): LocalePreference {
  return localePreference;
}

export function listLocales(): string[] {
  return Object.keys(CATALOGS);
}

/** Fixed options for the locale switcher. */
export const LOCALE_OPTIONS: {
  id: LocalePreference;
  shortKey?: string;
  short?: string;
  labelKey?: string;
  label?: string;
}[] = [
  { id: "system", shortKey: "sidebar.autoShort", labelKey: "sidebar.auto" },
  { id: "en", short: "EN", label: "English" },
  { id: "ru", short: "RU", label: "Русский" },
];

export function setLocalePreference(preference: LocalePreference): void {
  const nextPref =
    preference === "system" || preference === "en" || preference === "ru"
      ? preference
      : "system";
  const nextLocale = resolveLocale(nextPref);
  const changed = nextPref !== localePreference || nextLocale !== currentLocale;
  localePreference = nextPref;
  currentLocale = nextLocale;
  persistPreference(nextPref);
  if (changed) notify();
}

/** @deprecated Prefer setLocalePreference — kept for call-site clarity. */
export function setLocale(locale: string): void {
  if (locale === "system" || locale === "en" || locale === "ru") {
    setLocalePreference(locale);
    return;
  }
  setLocalePreference("en");
}

export function subscribeLocale(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function lookup(messages: LocaleMessages, key: string): string | undefined {
  const parts = key.split(".");
  let node: unknown = messages;
  for (const part of parts) {
    if (!node || typeof node !== "object") return undefined;
    node = (node as Record<string, unknown>)[part];
  }
  return typeof node === "string" ? node : undefined;
}

function interpolate(template: string, vars?: TranslateVars): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, name: string) => {
    const value = vars[name];
    return value === undefined || value === null ? `{${name}}` : String(value);
  });
}

export function t(key: string, vars?: TranslateVars, fallback?: string): string {
  const primary = lookup(CATALOGS[currentLocale] || en, key);
  const secondary = currentLocale === "en" ? undefined : lookup(en, key);
  const template = primary ?? secondary ?? fallback ?? key;
  return interpolate(template, vars);
}

export function useI18n(): {
  locale: string;
  localePreference: LocalePreference;
  t: typeof t;
  setLocale: typeof setLocalePreference;
  setLocalePreference: typeof setLocalePreference;
} {
  const locale = useSyncExternalStore(subscribeLocale, getLocale, () => "en");
  const localePreferenceValue = useSyncExternalStore(
    subscribeLocale,
    getLocalePreference,
    (): LocalePreference => "system",
  );
  return {
    locale,
    localePreference: localePreferenceValue,
    t,
    setLocale: setLocalePreference,
    setLocalePreference,
  };
}
