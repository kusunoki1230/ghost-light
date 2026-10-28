// Builds www/ (what the Android app and the online library serve) from app/.
import fs from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const app = path.join(root, "app");
const www = path.join(root, "www");
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(www, { recursive: true });

// Online library address, e.g. https://noki.github.io/ghost-light/content/
let remote = process.env.GL_REMOTE || "";
remote = remote.replace(/^https:\/\/([^.]+)\.github\.io/, (m, o) => `https://${o.toLowerCase()}.github.io`);

const page = fs.readFileSync(path.join(app, "ghost-light.html"), "utf8");
const head = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.5 system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
<script>window.GL_REMOTE=${JSON.stringify(remote)};</script>
<script src="app-shim.js"></script>
</head><body>`;
fs.writeFileSync(path.join(www, "index.html"), head + page + "\n</body></html>\n");
fs.copyFileSync(path.join(app, "app-shim.js"), path.join(www, "app-shim.js"));
fs.cpSync(path.join(app, "audio"), path.join(www, "audio"), { recursive: true });
fs.cpSync(path.join(app, "content"), path.join(www, "content"), { recursive: true });
fs.writeFileSync(path.join(www, ".nojekyll"), "");
console.log("www built; online library:", remote || "(none, bundled only)");
