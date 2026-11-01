"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSemanticIndex } from "@/components/use-semantic";

const KEY = "c-ref.openrouter-key";
const MODEL_KEY = "c-ref.openrouter-model";
const DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free";

export function AssistantPanel() {
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState(DEFAULT_MODEL);
  const [question, setQuestion] = useState("When should I use nullptr instead of NULL?");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<{ title: string; slug: string; score: number }[]>([]);
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "done">("idle");
  const [message, setMessage] = useState("");
  const { ready, error, search } = useSemanticIndex();

  useEffect(() => {
    setApiKey(window.localStorage.getItem(KEY) ?? "");
    setModel(window.localStorage.getItem(MODEL_KEY) || DEFAULT_MODEL);
  }, []);

  function saveKey() {
    window.localStorage.setItem(KEY, apiKey.trim());
    window.localStorage.setItem(MODEL_KEY, model.trim() || DEFAULT_MODEL);
    setMessage("Saved in this browser only. It is not sent to c.umutabali.com.");
  }

  function clearKey() {
    window.localStorage.removeItem(KEY);
    setApiKey("");
    setMessage("Key removed from localStorage.");
  }

  async function ask() {
    if (!apiKey.trim()) {
      setStatus("error");
      setMessage("Paste an OpenRouter key first. This site has no server-side secret.");
      return;
    }
    setStatus("loading");
    setAnswer("");
    setMessage("");
    try {
      const hits = await search(question, 5);
      const kept = hits.filter((hit) => hit.doc);
      setSources(kept.map((hit) => ({ title: hit.doc!.title, slug: hit.doc!.slug, score: hit.score })));
      const context = kept.map((hit, index) => `[${index + 1}] ${hit.doc!.title} (/reference/${hit.doc!.slug}/)\n${hit.doc!.excerpt}`).join("\n\n");
      const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey.trim()}`,
          "Content-Type": "application/json",
          "HTTP-Referer": "https://c.umutabali.com",
          "X-Title": "C Reference",
        },
        body: JSON.stringify({
          model: model.trim() || DEFAULT_MODEL,
          messages: [
            {
              role: "system",
              content: "You answer questions about ISO C using the reference excerpts. If the excerpts do not contain the answer, say so. Do not invent function signatures. Mention when a feature is C23.",
            },
            { role: "user", content: `Excerpts:\n${context}\n\nQuestion: ${question}` },
          ],
        }),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`OpenRouter returned ${response.status}. ${detail.slice(0, 240)}`);
      }
      const payload = await response.json() as { choices?: { message?: { content?: string } }[] };
      setAnswer(payload.choices?.[0]?.message?.content ?? "The model returned an empty answer.");
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "The request failed.");
    }
  }

  return (
    <div className="max-w-3xl space-y-4">
      <div className="rounded-2xl border border-dashed border-accent bg-elev p-4 text-sm">
        Beta. Retrieval uses the local embedding index. The answer call goes from your browser to OpenRouter with a key you supply. Nothing is stored on the server, because there is no server.
      </div>
      {error ? <p className="text-sm text-warn" role="alert">{error}</p> : null}
      {!ready && !error ? <p className="text-sm text-muted">Loading the local index…</p> : null}
      <label className="block text-sm font-semibold">
        OpenRouter key
        <Input className="mt-1" type="password" autoComplete="off" value={apiKey} onChange={(event) => setApiKey(event.target.value)} placeholder="sk-or-…" />
      </label>
      <label className="block text-sm font-semibold">
        Model
        <Input className="mt-1" value={model} onChange={(event) => setModel(event.target.value)} />
      </label>
      <div className="flex gap-2">
        <Button type="button" variant="outline" onClick={saveKey}>Save in this browser</Button>
        <Button type="button" variant="ghost" onClick={clearKey}>Forget key</Button>
      </div>
      <label className="block text-sm font-semibold">
        Question
        <textarea className="mt-1 min-h-28 w-full rounded-2xl border border-line bg-elev p-3 text-sm outline-none focus:ring-2 focus:ring-accent" value={question} onChange={(event) => setQuestion(event.target.value)} />
      </label>
      <Button type="button" onClick={() => void ask()} disabled={status === "loading" || !ready}>
        {status === "loading" ? "Retrieving and asking…" : "Ask"}
      </Button>
      {message ? <p className="text-sm text-warn" role="status">{message}</p> : null}
      {sources.length > 0 ? (
        <div>
          <h2 className="font-serif text-2xl">Retrieved pages</h2>
          <ul className="mt-2 space-y-1 text-sm">
            {sources.map((source) => (
              <li key={source.slug}>
                <Link className="text-accent" href={`/reference/${source.slug}/`}>{source.title}</Link>
                <span className="text-muted"> · {source.score.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {answer ? (
        <article className="rounded-2xl border border-line bg-elev p-4 whitespace-pre-wrap">{answer}</article>
      ) : null}
    </div>
  );
}
