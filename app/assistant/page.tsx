import { AssistantPanel } from "@/components/assistant-panel";

export const metadata = { title: "Assistant (beta)" };

export default function AssistantPage() {
  return (
    <main id="content" className="px-4 py-8 md:px-10">
      <p className="text-sm font-bold uppercase tracking-[0.14em] text-accent">Beta</p>
      <h1 className="mt-2 font-serif text-4xl">Ask the reference</h1>
      <p className="mt-2 max-w-2xl text-muted">
        The owner cannot use an Anthropic key here. Paste your own OpenRouter key, stored only in localStorage. The default model is nvidia/nemotron-3-ultra-550b-a55b:free. Context is the nearest pages from the local MiniLM index.
      </p>
      <div className="mt-6">
        <AssistantPanel />
      </div>
    </main>
  );
}
