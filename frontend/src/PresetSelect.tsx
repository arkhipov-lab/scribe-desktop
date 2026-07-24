import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import type { SummaryPresetOption } from "./vite-env";

interface PresetSelectProps {
  value: string;
  options: SummaryPresetOption[];
  disabled?: boolean;
  onChange: (id: string) => void;
}

function filterPresets(
  options: SummaryPresetOption[],
  query: string,
): SummaryPresetOption[] {
  const q = query.trim().toLowerCase();
  if (!q) return options;
  return options.filter(
    (preset) =>
      preset.label.toLowerCase().includes(q) || preset.id.toLowerCase().includes(q),
  );
}

export default function PresetSelect({
  value,
  options,
  disabled = false,
  onChange,
}: PresetSelectProps) {
  const listId = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);

  const selectedLabel =
    options.find((preset) => preset.id === value)?.label || value || "Select preset";
  const filtered = useMemo(() => filterPresets(options, query), [options, query]);

  useEffect(() => {
    if (!open) return;

    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }

    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    setHighlight(0);
    const id = window.requestAnimationFrame(() => inputRef.current?.focus());
    return () => window.cancelAnimationFrame(id);
  }, [open]);

  useEffect(() => {
    setHighlight(0);
  }, [query]);

  useEffect(() => {
    if (!open || !listRef.current) return;
    const item = listRef.current.querySelector<HTMLElement>(
      `[data-index="${highlight}"]`,
    );
    item?.scrollIntoView({ block: "nearest" });
  }, [highlight, open, filtered]);

  function openMenu() {
    if (disabled) return;
    setQuery("");
    setOpen(true);
  }

  function closeMenu() {
    setOpen(false);
    setQuery("");
  }

  function pick(id: string) {
    onChange(id);
    closeMenu();
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      if (!open) {
        openMenu();
        return;
      }
      setHighlight((i) => Math.min(i + 1, Math.max(filtered.length - 1, 0)));
      return;
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlight((i) => Math.max(i - 1, 0));
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      const preset = filtered[highlight];
      if (preset) pick(preset.id);
      return;
    }
    if (event.key === "Escape") {
      event.preventDefault();
      closeMenu();
    }
  }

  return (
    <div
      className={`language-combobox ${open ? "open" : ""} ${disabled ? "disabled" : ""}`}
      ref={rootRef}
    >
      {open ? (
        <input
          ref={inputRef}
          id="summary-preset"
          className="language-select language-search"
          type="text"
          role="combobox"
          aria-expanded="true"
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={
            filtered[highlight] ? `${listId}-${filtered[highlight].id}` : undefined
          }
          placeholder="Search preset…"
          value={query}
          disabled={disabled}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
        />
      ) : (
        <button
          type="button"
          id="summary-preset"
          className="language-select language-trigger"
          disabled={disabled}
          aria-haspopup="listbox"
          aria-expanded="false"
          onClick={openMenu}
        >
          {selectedLabel}
        </button>
      )}

      {open && (
        <ul
          ref={listRef}
          id={listId}
          className="language-menu"
          role="listbox"
          aria-label="Summary presets"
        >
          {filtered.length === 0 ? (
            <li className="language-empty" role="presentation">
              No matches
            </li>
          ) : (
            filtered.map((preset, index) => (
              <li key={preset.id} role="presentation">
                <button
                  type="button"
                  id={`${listId}-${preset.id}`}
                  data-index={index}
                  role="option"
                  aria-selected={preset.id === value}
                  className={`language-option ${index === highlight ? "highlight" : ""} ${
                    preset.id === value ? "selected" : ""
                  }`}
                  onMouseEnter={() => setHighlight(index)}
                  onClick={() => pick(preset.id)}
                >
                  {preset.label}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
