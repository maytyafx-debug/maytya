import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();
const docs = path.join(root, "docs");
const pagePath = path.join(docs, "shared-capabilities.html");
const html = fs.readFileSync(pagePath, "utf8");

const required = [
  ['Persian language', /<html[^>]*lang=["']fa["']/i],
  ['RTL direction', /<html[^>]*dir=["']rtl["']/i],
  ['viewport metadata', /name=["']viewport["']/i],
  ['page title', /<title>[^<]+<\/title>/i],
  ['shared design tokens', /href=["']metatya-core\.css["']/i],
  ['shared page stylesheet', /href=["']metatya-shared-pages\.css["']/i],
  ['shared page script', /src=["']metatya-shared-pages\.js["']/i],
  ['main landmark', /<main\b/i],
  ['capabilities section', /id=["']capabilities["']/i],
  ['architecture section', /id=["']architecture["']/i],
  ['products section', /id=["']products["']/i],
  ['AI agents capability', /هوش مصنوعی و سیستم ایجنت‌ها/],
  ['backup and recovery capability', /پشتیبان‌گیری و بازیابی امن/],
  ['quality capability', /تست، پایش و ارزیابی کیفیت/],
  ['Sports OS product', /METATYA Sports OS/],
  ['Business OS product', /METATYA Business OS/],
];

for (const [label, pattern] of required) {
  assert.match(html, pattern, `Missing required page element: ${label}`);
}

const ids = [...html.matchAll(/\bid=["']([^"']+)["']/g)].map(match => match[1]);
assert.equal(ids.length, new Set(ids).size, "Duplicate HTML id attribute found");

const localFiles = [...html.matchAll(/(?:href|src)=["']([^"'#][^"']*)["']/g)]
  .map(match => match[1])
  .filter(value => !/^(?:https?:|mailto:|tel:|data:|javascript:)/i.test(value));
for (const value of localFiles) {
  const clean = value.split(/[?#]/, 1)[0];
  if (!clean) continue;
  assert.ok(fs.existsSync(path.join(docs, clean)), `Broken local asset/link: ${value}`);
}

const anchors = [...html.matchAll(/href=["']#([^"']+)["']/g)].map(match => match[1]);
for (const anchor of anchors) {
  assert.ok(ids.includes(anchor), `Broken in-page anchor: #${anchor}`);
}

const css = fs.readFileSync(path.join(docs, "metatya-shared-pages.css"), "utf8");
const js = fs.readFileSync(path.join(docs, "metatya-shared-pages.js"), "utf8");
assert.match(css, /prefers-reduced-motion/, "Reduced-motion support is required");
assert.match(css, /:focus-visible/, "Visible keyboard focus is required");
assert.match(js, /aria-expanded/, "Accessible mobile menu state is required");

console.log(`PASS: ${required.length} page checks, ${ids.length} unique IDs, ${localFiles.length} local assets, ${anchors.length} anchors.`);
