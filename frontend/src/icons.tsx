/** Small stroke icons for action buttons (currentColor). */

type IconProps = {
  className?: string;
};

const stroke = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.75,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export function IconSave({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M12 3v12" />
      <path {...stroke} d="M8 11l4 4 4-4" />
      <path {...stroke} d="M5 19h14" />
    </svg>
  );
}

export function IconExport({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M14 3h7v7" />
      <path {...stroke} d="M10 14L21 3" />
      <path {...stroke} d="M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5" />
    </svg>
  );
}

export function IconCopy({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <rect {...stroke} x="8" y="8" width="12" height="12" rx="2" />
      <path {...stroke} d="M4 16V6a2 2 0 0 1 2-2h10" />
    </svg>
  );
}

export function IconCheck({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M5 12.5l4.5 4.5L19 7" />
    </svg>
  );
}

export function IconSparkles({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M12 3v3M12 18v3M3 12h3M18 12h3" />
      <path {...stroke} d="M6.2 6.2l2.1 2.1M15.7 15.7l2.1 2.1M17.8 6.2l-2.1 2.1M8.3 15.7l-2.1 2.1" />
      <circle {...stroke} cx="12" cy="12" r="2.5" />
    </svg>
  );
}

export function IconRefresh({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M20 12a8 8 0 1 1-2.2-5.5" />
      <path {...stroke} d="M20 4v5h-5" />
    </svg>
  );
}

export function IconPlay({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        stroke="none"
        d="M8.5 5.8v12.4c0 .7.75 1.1 1.35.7l9.2-6.2a.85.85 0 0 0 0-1.4l-9.2-6.2a.85.85 0 0 0-1.35.7Z"
      />
    </svg>
  );
}

export function IconPause({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <rect fill="currentColor" stroke="none" x="6.5" y="5" width="3.5" height="14" rx="1" />
      <rect fill="currentColor" stroke="none" x="14" y="5" width="3.5" height="14" rx="1" />
    </svg>
  );
}

export function IconPlus({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path {...stroke} d="M12 5v14" />
      <path {...stroke} d="M5 12h14" />
    </svg>
  );
}

export function IconStop({ className }: IconProps) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <rect fill="currentColor" stroke="none" x="6.5" y="6.5" width="11" height="11" rx="1.5" />
    </svg>
  );
}
