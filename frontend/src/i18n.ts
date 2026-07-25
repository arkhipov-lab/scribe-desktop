import { useSyncExternalStore } from "react";
import en from "./locales/en.json";
import ru from "./locales/ru.json";

export type LocaleMessages = typeof en;
export type TranslateVars = Record<string, string | number>;

const CATALOGS: Record<string, LocaleMessages> = {
  en,
  ru,
};

let currentLocale = detectLocale();
const listeners = new Set<() => void>();

function detectLocale(): string {
  try {
    const stored = window.localStorage?.getItem("scribe.locale");
    if (stored && CATALOGS[stored]) return stored;
  } catch {
    // ignore storage failures
  }
  const nav = (navigator.language || "en").toLowerCase();
  const short = nav.split("-")[0] || "en";
  if (CATALOGS[short]) return short;
  return "en";
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

function notify(): void {
  listeners.forEach((fn) => fn());
}

export function getLocale(): string {
  return currentLocale;
}

export function listLocales(): string[] {
  return Object.keys(CATALOGS);
}

/** Short labels for the locale switcher (native names, not translated). */
export const LOCALE_OPTIONS: { id: string; short: string; label: string }[] = [
  { id: "en", short: "EN", label: "English" },
  { id: "ru", short: "RU", label: "Русский" },
];


export function setLocale(locale: string): void {
  const next = CATALOGS[locale] ? locale : "en";
  if (next === currentLocale) return;
  currentLocale = next;
  try {
    window.localStorage?.setItem("scribe.locale", next);
  } catch {
    // ignore
  }
  notify();
}

export function subscribeLocale(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function t(key: string, vars?: TranslateVars, fallback?: string): string {
  const primary = lookup(CATALOGS[currentLocale] || en, key);
  const secondary = currentLocale === "en" ? undefined : lookup(en, key);
  const template = primary ?? secondary ?? fallback ?? key;
  return interpolate(template, vars);
}

export function useI18n(): {
  locale: string;
  t: typeof t;
  setLocale: typeof setLocale;
} {
  const locale = useSyncExternalStore(
    subscribeLocale,
    getLocale,
    () => "en",
  );
  return { locale, t, setLocale };
}
