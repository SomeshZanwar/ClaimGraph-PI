import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const base = (process.env.PUBLIC_BASE_URL || "http://localhost:5173").replace(/\/$/, "");
const routes = ["/", "/about", "/privacy", "/terms", "/support", "/login", "/signup"];

const xml = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
  ...routes.map((route) => `  <url><loc>${base}${route}</loc></url>`),
  "</urlset>",
  "",
].join("\n");

const robots = [
  "User-agent: *",
  "Allow: /",
  "Disallow: /queue",
  "Disallow: /cases/",
  "Disallow: /providers/",
  `Sitemap: ${base}/sitemap.xml`,
  "",
].join("\n");

const publicDir = resolve("public");
await mkdir(publicDir, { recursive: true });
await writeFile(resolve(publicDir, "sitemap.xml"), xml, "utf8");
await writeFile(resolve(publicDir, "robots.txt"), robots, "utf8");
