import type { InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-full border border-line bg-elev px-4 text-sm text-ink outline-none placeholder:text-muted focus:ring-2 focus:ring-accent",
        className,
      )}
      {...props}
    />
  );
}
