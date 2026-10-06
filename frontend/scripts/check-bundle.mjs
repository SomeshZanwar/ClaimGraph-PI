import { readdir, stat } from "node:fs/promises";
import { resolve } from "node:path";

const assetsDir = resolve("dist/assets");
const names = await readdir(assetsDir);
const jsFiles = names.filter((name) => name.endsWith(".js"));

if (jsFiles.length === 0) {
  throw new Error("No JavaScript build artifacts found");
}

const sizes = [];
for (const name of jsFiles) {
  const fileStat = await stat(resolve(assetsDir, name));
  sizes.push({ name, bytes: fileStat.size });
}

const initial = sizes.find(({ name }) => name.startsWith("index-"));
if (!initial) {
  throw new Error("Initial application bundle was not found");
}

const initialLimit = 400 * 1024;
const chunkLimit = 550 * 1024;

if (initial.bytes > initialLimit) {
  throw new Error(
    `Initial JavaScript bundle is ${initial.bytes} bytes; limit is ${initialLimit}`,
  );
}

const oversized = sizes.filter(({ bytes }) => bytes > chunkLimit);
if (oversized.length > 0) {
  throw new Error(
    "Oversized JavaScript chunks: " +
      oversized.map(({ name, bytes }) => `${name}=${bytes}`).join(", "),
  );
}

console.log(
  "Bundle size check passed:",
  sizes.map(({ name, bytes }) => `${name}=${bytes}`).join(", "),
);
