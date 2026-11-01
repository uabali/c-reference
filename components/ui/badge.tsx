import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const tones: Record<string, string> = {
  Beginner: "bg-good/15 text-good",
  Intermediate: "bg-accent/15 text-accent",
  Advanced: "bg-ink text-bg",
  neutral: "bg-chip text-ink",
};

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: ReactNode;
  tone?: string;
  className?: string;
}) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold", tones[tone] ?? tones.neutral, className)}>
      {children}
    </span>
  );
}
