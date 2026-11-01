"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

export function CodeEnhance() {
  const pathname = usePathname();
  useEffect(() => {
    const blocks = document.querySelectorAll("pre.codeblock");
    const cleanups: Array<() => void> = [];
    blocks.forEach((block) => {
      if (block.querySelector(".copy-code")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "copy-code";
      button.textContent = "Copy";
      button.addEventListener("click", async () => {
        const code = block.querySelector("code")?.textContent ?? "";
        try {
          await navigator.clipboard.writeText(code);
          button.textContent = "Copied";
          window.setTimeout(() => {
            button.textContent = "Copy";
          }, 1200);
        } catch {
          button.textContent = "Copy failed";
        }
      });
      block.append(button);
      cleanups.push(() => button.remove());
    });
    return () => cleanups.forEach((fn) => fn());
  }, [pathname]);
  return null;
}
