import { AlertCircle, CircleCheck, LoaderCircle } from "lucide-react";
import { type ReactNode } from "react";

type StatusPanelProps = { children: ReactNode; tone?: "error" | "loading" | "success" };
const icons = { error: AlertCircle, loading: LoaderCircle, success: CircleCheck };

export function StatusPanel({ children, tone = "loading" }: StatusPanelProps) {
  const Icon = icons[tone];
  const toneClass = tone === "error" ? "text-[var(--mm-danger)]" : tone === "success" ? "text-[var(--mm-success)]" : "text-[var(--mm-accent)]";

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-[var(--mm-border)] bg-[var(--mm-surface)] p-4 text-sm text-[var(--mm-text-muted)]" role={tone === "error" ? "alert" : "status"}>
      <Icon aria-hidden="true" className={`size-5 shrink-0 ${toneClass} ${tone === "loading" ? "animate-spin" : ""}`} />
      {children}
    </div>
  );
}
