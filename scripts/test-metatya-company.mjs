import { readFileSync, existsSync } from "node:fs";

const html = readFileSync("docs/metatya.html", "utf8");
const css = readFileSync("docs/metatya-company.css", "utf8");
const js = readFileSync("docs/metatya-company.js", "utf8");

const checks = [
  ["Persian RTL document", /<html lang="fa" dir="rtl">/.test(html)],
  ["Unique element IDs", (() => {
    const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
    return ids.length === new Set(ids).size;
  })()],
  ["Main landmarks", /<main id="main">/.test(html) && /<header/.test(html) && /<footer/.test(html)],
  ["Core sections", ["vision", "ecosystem", "foundation", "principles", "about"].every(id => html.includes(`id="${id}"`))],
  ["Product status transparency", /در حال توسعه/.test(html) && /مسیر محصول/.test(html) && /شفافیت در وضعیت/.test(html)],
  ["Data isolation principle", /داده‌های هر صنعت و هر سازمان مستقل/.test(html) || /داده نیست/.test(html)],
  ["Founder profile", /آیت قمری/.test(html) && /بنیان‌گذار و مدیرعامل/.test(html)],
  ["Responsive layouts", /@media\(max-width:720px\)/.test(css) && /@media\(max-width:480px\)/.test(css)],
  ["Reduced motion support", /prefers-reduced-motion:reduce/.test(css)],
  ["Visible keyboard focus", /:focus-visible/.test(css)],
  ["Accessible mobile menu", /aria-expanded/.test(html) && /aria-controls="mobile-menu"/.test(html) && /aria-expanded/.test(js)],
  ["Year fallback behavior", /data-year/.test(html) && /getFullYear/.test(js)],
  ["Academy cross-link", /href="index.html"/.test(html)],
  ["Shared foundation disclaimer", /معنی پیاده‌سازی یا فعال بودن/.test(html)]
];

const localTargets = [...html.matchAll(/(?:href|src)="([^"]+)"/g)]
  .map(m => m[1])
  .filter(value => !/^(https?:|mailto:|tel:|#|data:|javascript:)/i.test(value))
  .map(value => value.split("#")[0].split("?")[0])
  .filter(Boolean);
for (const target of localTargets) {
  const path = target.startsWith("/") ? `docs${target}` : `docs/${target}`;
  checks.push([`Local target exists: ${target}`, existsSync(path)]);
}
const failed = checks.filter(([, ok]) => !ok);
for (const [name, ok] of checks) console.log(`${ok ? "PASS" : "FAIL"} ${name}`);
console.log(`\\n${checks.length - failed.length}/${checks.length} checks passed`);
if (failed.length) process.exit(1);
