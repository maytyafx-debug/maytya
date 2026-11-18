import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";

const html = readFileSync("docs/metatya.html", "utf8");
const css = readFileSync("docs/metatya-company.css", "utf8");
const js = readFileSync("docs/metatya-company.js", "utf8");
const templatePath = "docs/design-system/metatya-corporate-page-template.html";
const template = readFileSync(templatePath, "utf8");
const designSystem = readFileSync("docs/design-system/metatya-corporate-design-system.md", "utf8");

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
  ["Shared foundation disclaimer", /معنی پیاده‌سازی یا فعال بودن/.test(html)],
  ["Reusable template uses Persian RTL", /<html lang="fa" dir="rtl">/.test(template)],
  ["Reusable template uses canonical CSS and JS", template.includes('href="../metatya-company.css"') && template.includes('src="../metatya-company.js"')],
  ["Reusable template has accessible page shell", /class="skip-link" href="#main"/.test(template) && /<main id="main">/.test(template) && /aria-controls="mobile-menu"/.test(template)],
  ["Reusable template uses canonical components", [".hero", ".section-heading", ".product-card", ".site-footer"].every(token => template.includes(token))],
  ["Design system documents canonical visual tokens", ["#050807", "#00ff9d", "#c5d0ca", "metatya-company.css"].every(token => designSystem.includes(token))],
  ["Design system preserves Academy separation and change control", /METATYA Academy/.test(designSystem) && /explicit approval/i.test(designSystem)]
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

const templateTargets = [...template.matchAll(/(?:href|src)="([^"]+)"/g)]
  .map(m => m[1])
  .filter(value => !/^(https?:|mailto:|tel:|#|data:|javascript:)/i.test(value))
  .map(value => value.split("#")[0].split("?")[0])
  .filter(Boolean);
for (const target of templateTargets) {
  const path = resolve(dirname(templatePath), target);
  checks.push([`Template local target exists: ${target}`, existsSync(path)]);
}

const failed = checks.filter(([, ok]) => !ok);
for (const [name, ok] of checks) console.log(`${ok ? "PASS" : "FAIL"} ${name}`);
console.log(`\n${checks.length - failed.length}/${checks.length} checks passed`);
if (failed.length) process.exit(1);
