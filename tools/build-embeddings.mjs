import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, pipeline } from "@xenova/transformers";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const docsPath = path.join(root, "public/search/documents.json");
const modelDir = path.join(root, "public/models");
const outBin = path.join(root, "public/search/embeddings.bin");
const outMeta = path.join(root, "public/search/embedding-meta.json");

env.allowRemoteModels = false;
env.allowLocalModels = true;
env.localModelPath = modelDir;
env.backends.onnx.wasm.numThreads = 1;

const docs = JSON.parse(fs.readFileSync(docsPath, "utf8"));
const extractor = await pipeline("feature-extraction", "Xenova/all-MiniLM-L6-v2", {
  quantized: true,
});

const probe = await extractor("dimension probe", { pooling: "mean", normalize: true });
const dim = probe.data.length;
const vectors = new Float32Array(docs.length * dim);

for (let i = 0; i < docs.length; i += 1) {
  const text = String(docs[i].text || docs[i].title).slice(0, 1200);
  const output = await extractor(text, { pooling: "mean", normalize: true });
  vectors.set(output.data, i * dim);
  if (i % 25 === 0) console.log(`embedded ${i}/${docs.length}`);
}

fs.writeFileSync(outBin, Buffer.from(vectors.buffer));
fs.writeFileSync(
  outMeta,
  JSON.stringify(
    {
      model: "Xenova/all-MiniLM-L6-v2",
      dim,
      count: docs.length,
      normalized: true,
    },
    null,
    2,
  ) + "\n",
);
console.log(`wrote ${docs.length} x ${dim} embeddings`);
