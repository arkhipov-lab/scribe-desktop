/**
 * Extract the Action items section from summary markdown.
 * Headings mirror backend/summarizer.py meeting_notes localization + English presets.
 */

/** Known Action items heading titles (exact, case-insensitive match). */
export const ACTION_ITEM_HEADINGS: readonly string[] = [
  "Action items",
  "Задачи",
  "Задачі",
  "Aufgaben",
  "Actions",
  "Acciones",
  "Azioni",
  "Ações",
  "Zadania",
  "Aksiyonlar",
  "待办",
  "アクション",
  "할 일",
];

const HEADING_RE = /^(#{1,6})\s+(.+?)\s*$/;

function normalizeTitle(title: string): string {
  return title.replace(/\s+/g, " ").trim().toLowerCase();
}

const ACTION_ITEM_SET = new Set(
  ACTION_ITEM_HEADINGS.map((h) => normalizeTitle(h)),
);

function isActionItemsHeading(title: string): boolean {
  // Strip optional trailing punctuation / markdown emphasis leftovers.
  const cleaned = title.replace(/^[*_]+|[*_]+$/g, "").trim();
  return ACTION_ITEM_SET.has(normalizeTitle(cleaned));
}

/**
 * Returns the Action items section body (without the heading), or null if
 * the section is missing or empty after trim.
 */
export function extractActionItems(summary: string): string | null {
  const text = (summary || "").replace(/\r\n/g, "\n");
  if (!text.trim()) return null;

  const lines = text.split("\n");
  let start = -1;
  let level = 0;

  for (let i = 0; i < lines.length; i++) {
    const match = HEADING_RE.exec(lines[i]);
    if (!match) continue;
    const title = match[2];
    if (!isActionItemsHeading(title)) continue;
    start = i + 1;
    level = match[1].length;
    break;
  }

  if (start < 0) {
    // No known Action items heading → unavailable (do not treat heading-less
    // bodies as action items; that mis-labels other presets).
    return null;
  }

  let end = lines.length;
  for (let i = start; i < lines.length; i++) {
    const match = HEADING_RE.exec(lines[i]);
    if (!match) continue;
    if (match[1].length <= level) {
      end = i;
      break;
    }
  }

  const body = lines.slice(start, end).join("\n").trim();
  if (!body || isPlaceholderOnly(body)) return null;
  return body;
}

function isPlaceholderOnly(body: string): boolean {
  const compact = body.replace(/^[-*+]\s+/gm, "").trim().toLowerCase();
  return (
    compact === "" ||
    compact === "none" ||
    compact === "n/a" ||
    compact === "нет" ||
    compact === "немає" ||
    compact === "keine" ||
    compact === "aucune" ||
    compact === "ninguna" ||
    compact === "nessuna" ||
    compact === "nenhuma" ||
    compact === "brak" ||
    compact === "yok" ||
    compact === "无" ||
    compact === "なし" ||
    compact === "없음" ||
    compact === "short bullets, or none" ||
    compact === "concise bullets grounded in the transcript, or none"
  );
}
