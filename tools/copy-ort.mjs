import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.join(root, "node_modules/onnxruntime-web/dist");
const dest = path.join(root, "public/ort");
fs.mkdirSync(dest, { recursive: true });
for (const name of fs.readdirSync(source)) {
  if (name.endsWith(".wasm")) {
    fs.copyFileSync(path.join(source, name), path.join(dest, name));
  }
}
console.log("copied onnxruntime wasm into public/ort");
