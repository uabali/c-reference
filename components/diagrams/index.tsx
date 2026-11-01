"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";

export function Diagram({ id }: { id: string }) {
  if (id === "stack-heap") return <StackHeap />;
  if (id === "pointers") return <Pointers />;
  if (id === "arrays") return <Arrays />;
  if (id === "padding") return <Padding />;
  if (id === "function-pointers") return <FunctionPointers />;
  if (id === "translation") return <Translation />;
  return null;
}

function Frame({ title, children, caption }: { title: string; children: ReactNode; caption: string }) {
  return (
    <figure className="rounded-2xl border border-line bg-bg p-3">
      <figcaption className="mb-2 font-serif text-xl">{title}</figcaption>
      {children}
      <p className="mt-2 text-sm text-muted">{caption}</p>
    </figure>
  );
}

export function StackHeap() {
  const [frames, setFrames] = useState<string[]>(["main"]);
  const [heap, setHeap] = useState<{ id: number; freed: boolean }[]>([]);
  const next = heap.length + 1;
  return (
    <Frame
      title="Stack and heap"
      caption="Returning a function destroys its stack frame. A block from malloc stays until free. Freeing NULL is a no-op; freeing twice is undefined."
    >
      <div className="mb-3 flex flex-wrap gap-2">
        <Button size="sm" onClick={() => setFrames((items) => [...items, items.length === 1 ? "helper" : `frame ${items.length}`])}>Call</Button>
        <Button size="sm" variant="outline" onClick={() => setFrames((items) => (items.length > 1 ? items.slice(0, -1) : items))}>Return</Button>
        <Button size="sm" variant="outline" onClick={() => setHeap((items) => [...items, { id: next, freed: false }])}>malloc</Button>
        <Button size="sm" variant="outline" onClick={() => setHeap((items) => {
          const index = items.findIndex((item) => !item.freed);
          if (index < 0) return items;
          return items.map((item, i) => (i === index ? { ...item, freed: true } : item));
        })}>free</Button>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <p className="mb-1 text-xs font-bold uppercase tracking-wide text-muted">Stack</p>
          <div className="flex min-h-40 flex-col-reverse gap-1 rounded-xl border border-line bg-elev p-2">
            {frames.map((name, index) => (
              <div key={`${name}-${index}`} className="rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-white">
                {name}
                <span className="mt-1 block text-xs font-normal opacity-80">locals live here</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="mb-1 text-xs font-bold uppercase tracking-wide text-muted">Heap</p>
          <div className="flex min-h-40 flex-wrap content-start gap-2 rounded-xl border border-dashed border-line bg-elev p-2">
            {heap.length === 0 ? <p className="text-sm text-muted">No allocations yet.</p> : null}
            {heap.map((block) => (
              <div key={block.id} className={`rounded-lg px-3 py-2 text-sm ${block.freed ? "bg-chip text-muted line-through" : "bg-accent2 text-white"}`}>
                block {block.id}
              </div>
            ))}
          </div>
        </div>
      </div>
    </Frame>
  );
}

export function Pointers() {
  const cells = [4, 8, 15, 16, 23, 42];
  const [index, setIndex] = useState(1);
  const base = 0x1000;
  const address = base + index * 4;
  return (
    <Frame
      title="Pointer arithmetic"
      caption="If p points at an int, p + 1 advances one int, not one byte. The address is base + index * sizeof(int). Dereferencing outside the array is undefined."
    >
      <div className="mb-3 flex gap-2">
        <Button size="sm" variant="outline" onClick={() => setIndex((value) => Math.max(0, value - 1))}>p - 1</Button>
        <Button size="sm" onClick={() => setIndex((value) => Math.min(cells.length - 1, value + 1))}>p + 1</Button>
      </div>
      <svg viewBox="0 0 640 150" className="w-full" role="img" aria-label="Six integer cells and a pointer">
        {cells.map((value, i) => (
          <g key={value} transform={`translate(${20 + i * 100} 40)`}>
            <rect width="84" height="48" rx="8" fill={i === index ? "var(--accent)" : "var(--chip)"} />
            <text x="42" y="30" textAnchor="middle" fill={i === index ? "#fff" : "var(--ink)"} fontSize="16">{value}</text>
            <text x="42" y="68" textAnchor="middle" fill="var(--muted)" fontSize="11">0x{(base + i * 4).toString(16)}</text>
          </g>
        ))}
        <polygon points={`${62 + index * 100},28 ${54 + index * 100},14 ${70 + index * 100},14`} fill="var(--accent)" />
        <text x={62 + index * 100} y="12" textAnchor="middle" fill="var(--accent)" fontSize="12">p</text>
      </svg>
      <p className="font-mono text-sm">p[{index}] = {cells[index]} · address 0x{address.toString(16)} · *p reads {cells[index]}</p>
    </Frame>
  );
}

export function Arrays() {
  const [mode, setMode] = useState<"array" | "pointer">("array");
  const cells = ["H", "i", "\\0"];
  return (
    <Frame
      title="Arrays and strings in memory"
      caption={mode === "array"
        ? "char s[] = \"Hi\" owns four bytes, including the terminator. sizeof s is 3 and the cells are writable."
        : "char *p = \"Hi\" points at a static literal. sizeof p is the pointer width. Writing through p is undefined."}
    >
      <div className="mb-3 flex gap-2">
        <Button size="sm" variant={mode === "array" ? "default" : "outline"} onClick={() => setMode("array")}>char s[] = &quot;Hi&quot;</Button>
        <Button size="sm" variant={mode === "pointer" ? "default" : "outline"} onClick={() => setMode("pointer")}>char *p = &quot;Hi&quot;</Button>
      </div>
      <div className="flex flex-wrap items-end gap-2">
        {cells.map((cell, index) => (
          <div key={cell} className={`grid h-16 w-16 place-items-center rounded-xl border text-lg font-mono ${mode === "pointer" ? "border-dashed border-warn bg-chip" : "border-line bg-elev"}`}>
            {cell === "\\0" ? "\\0" : cell}
            <span className="text-[10px] text-muted">[{index}]</span>
          </div>
        ))}
        {mode === "pointer" ? <div className="mb-3 ml-2 text-sm text-warn">read-only literal</div> : <div className="mb-3 ml-2 text-sm text-good">writable array</div>}
      </div>
      <p className="mt-3 font-mono text-sm">
        {mode === "array" ? "sizeof s == 3 · strlen(s) == 2" : "sizeof p == sizeof(char *) · strlen(p) == 2"}
      </p>
    </Frame>
  );
}

const TYPES = ["char", "short", "int", "double"] as const;
type FieldType = (typeof TYPES)[number];
const SIZE: Record<FieldType, number> = { char: 1, short: 2, int: 4, double: 8 };

function layoutFields(fields: { name: string; type: FieldType }[]) {
  let offset = 0;
  let align = 1;
  const placed = fields.map((field) => {
    const size = SIZE[field.type];
    align = Math.max(align, size);
    const pad = (size - (offset % size)) % size;
    offset += pad;
    const start = offset;
    offset += size;
    return { ...field, start, size, pad };
  });
  const tail = offset === 0 ? 0 : (align - (offset % align)) % align;
  return { placed, bytes: offset + tail, align, tail };
}

export function Padding() {
  const [fields, setFields] = useState<{ name: string; type: FieldType }[]>([
    { name: "tag", type: "char" },
    { name: "count", type: "int" },
    { name: "flag", type: "char" },
    { name: "value", type: "double" },
  ]);
  const layout = useMemo(() => layoutFields(fields), [fields]);
  return (
    <Frame
      title="Struct padding and alignment"
      caption="On the LP64 ABI used by gcc and clang for x86-64 Linux, each field is aligned to its size and the struct is padded to its strictest alignment. Reordering often shrinks the object."
    >
      <div className="mb-3 flex flex-wrap gap-2">
        <Button size="sm" onClick={() => setFields([
          { name: "value", type: "double" },
          { name: "count", type: "int" },
          { name: "tag", type: "char" },
          { name: "flag", type: "char" },
        ])}>Pack by size</Button>
        <Button size="sm" variant="outline" onClick={() => setFields([
          { name: "tag", type: "char" },
          { name: "count", type: "int" },
          { name: "flag", type: "char" },
          { name: "value", type: "double" },
        ])}>Naive order</Button>
        <Button size="sm" variant="outline" onClick={() => setFields((items) => [...items, { name: `f${items.length}`, type: "short" }])}>Add short</Button>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        {fields.map((field, index) => (
          <label key={`${field.name}-${index}`} className="rounded-xl border border-line bg-elev px-2 py-1 text-xs">
            {field.name}
            <select
              className="ml-2 bg-transparent"
              value={field.type}
              aria-label={`Type of ${field.name}`}
              onChange={(event) => setFields((items) => items.map((item, i) => i === index ? { ...item, type: event.target.value as FieldType } : item))}
            >
              {TYPES.map((type) => <option key={type}>{type}</option>)}
            </select>
          </label>
        ))}
      </div>
      <div className="flex flex-wrap gap-1">
        {Array.from({ length: layout.bytes }, (_, byte) => {
          const field = layout.placed.find((item) => byte >= item.start && byte < item.start + item.size);
          return (
            <div key={byte} title={field ? field.name : "padding"} className={`grid h-8 w-8 place-items-center rounded text-[10px] ${field ? "bg-accent text-white" : "bg-chip text-muted"}`}>
              {byte}
            </div>
          );
        })}
      </div>
      <p className="mt-3 font-mono text-sm">sizeof = {layout.bytes}, alignof = {layout.align}, tail padding = {layout.tail}</p>
    </Frame>
  );
}

const OPS = {
  add: (a: number, b: number) => a + b,
  mul: (a: number, b: number) => a * b,
  max: (a: number, b: number) => (a > b ? a : b),
};

export function FunctionPointers() {
  const [name, setName] = useState<keyof typeof OPS>("add");
  const result = OPS[name](2, 3);
  return (
    <Frame
      title="Function pointers"
      caption="A function pointer is an object. You can store it, pass it, and call through it. qsort does exactly this with a comparator of type int (*)(const void *, const void *)."
    >
      <div className="mb-3 flex flex-wrap gap-2">
        {(Object.keys(OPS) as (keyof typeof OPS)[]).map((key) => (
          <Button key={key} size="sm" variant={name === key ? "default" : "outline"} onClick={() => setName(key)}>{key}</Button>
        ))}
      </div>
      <svg viewBox="0 0 560 120" className="w-full" role="img" aria-label="Function pointer targeting a function">
        <rect x="20" y="36" width="150" height="48" rx="10" fill="var(--ink)" />
        <text x="95" y="65" textAnchor="middle" fill="var(--bg)" fontSize="14">int (*fp)(int, int)</text>
        <line x1="170" y1="60" x2="250" y2="60" stroke="var(--accent)" strokeWidth="3" />
        <polygon points="250,60 238,54 238,66" fill="var(--accent)" />
        <rect x="260" y="28" width="250" height="64" rx="10" fill="var(--accent)" />
        <text x="385" y="56" textAnchor="middle" fill="#fff" fontSize="16">{name}(2, 3)</text>
        <text x="385" y="76" textAnchor="middle" fill="#fff" fontSize="14">returns {result}</text>
      </svg>
      <p className="font-mono text-sm">fp = {name}; result = fp(2, 3); /* {result} */</p>
    </Frame>
  );
}

export function Translation() {
  const phases = [
    ["1–4", "Physical source, trigraphs, line splicing, comments"],
    ["5–6", "Preprocessor: includes, macros, #embed, conditionals"],
    ["7", "Tokens become the translation unit the compiler parses"],
    ["8", "Object code, then the linker builds the image"],
  ];
  return (
    <Frame
      title="How a C program is translated"
      caption="cppreference lists eight translation phases. The picture collapses them into the four moments you actually feel: text, preprocessor, compiler, linker."
    >
      <ol className="grid gap-2 md:grid-cols-4">
        {phases.map(([step, text], index) => (
          <li key={step} className="rounded-xl border border-line bg-elev p-3">
            <span className="font-mono text-xs text-accent">Phase {step}</span>
            <p className="mt-1 text-sm">{text}</p>
            {index < phases.length - 1 ? <span className="mt-2 block text-xs text-muted md:hidden">then</span> : null}
          </li>
        ))}
      </ol>
      <pre className="mt-3 overflow-x-auto rounded-xl bg-code p-3 font-mono text-xs text-muted">{`flowchart LR
  source[Source files] --> pp[Preprocessor]
  pp --> cc[Compiler]
  cc --> ld[Linker]
  ld --> image[Program image]`}</pre>
    </Frame>
  );
}
