import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";

const html = readFileSync("docs/metatya.html", "utf8");
const css = readFileSync("docs/metatya-company.css", "utf8");
const js = readFileSync("docs/metatya-company.js", "utf8");
const templatePath = "docs/design-system/metatya-corporate-page-template.html";
const template = readFileSync(templatePath, "utf8");
const designSystem = readFileSync("docs/design-system/metatya-corporate-design-system.md", "utf8");
const corporatePages = [
  "docs/metatya.html",
  "docs/company-ecosystem.html",
  "docs/company-technology.html",
  "docs/company-trust.html",
  "docs/company-contact.html"
].map(path => ({ path, html: readFileSync(path, "utf8") }));

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
  ["Reusable template uses canonical components", (() => {
    // Verify each shared component is present in template markup and canonical CSS.
    const classes = new Set(
      [...template.matchAll(/\bclass="([^"]+)"/g)]
        .flatMap(match => match[1].split(/\s+/))
    );
    const components = ["hero", "section-heading", "product-card", "site-footer"];
    const selectors = [".hero{", ".section-heading{", ".product-card{", ".site-footer{"];
    return components.every((name, index) => classes.has(name) && css.includes(selectors[index]));
  })()],
  ["Integrated corporate pages share canonical shell", corporatePages.every(({html}) =>
    /<html lang="fa" dir="rtl">/.test(html) &&
    /metatya-company.css/.test(html) &&
    /metatya-company.js/.test(html) &&
    /<main id="main">/.test(html) &&
    /class="site-footer"/.test(html)
  )],
  ["Corporate pages link to one another", corporatePages.slice(1).every(({html}) =>
    ["metatya.html", "company-ecosystem.html", "company-technology.html", "company-trust.html", "company-contact.html"]
      .filter(target => !html.includes(target))
      .length <= 1
  )],
  ["Corporate homepage exposes integrated page navigation", ["company-ecosystem.html", "company-technology.html", "company-trust.html", "company-contact.html"].every(path => html.includes(path))],
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

for (const {path, html: pageHtml} of corporatePages.slice(1)) {
  const targets = [...pageHtml.matchAll(/(?:href|src)="([^"]+)"/g)]
    .map(match => match[1])
    .filter(value => !/^(https?:|mailto:|tel:|#|data:|javascript:)/i.test(value))
    .map(value => value.split("#")[0].split("?")[0])
    .filter(Boolean);
  for (const target of targets) {
    const targetPath = target.startsWith("/") ? `docs${target}` : `docs/${target}`;
    checks.push([`${path} local target exists: ${target}`, existsSync(targetPath)]);
  }
}


const refinementCssPath = "docs/metatya-corporate-refinement.css";
const refinementCss = readFileSync(refinementCssPath, "utf8");
checks.push(["Corporate refinement stylesheet exists", existsSync(refinementCssPath)]);
checks.push(["Refinement stylesheet respects reduced motion", /prefers-reduced-motion:reduce/.test(refinementCss)]);
checks.push(["Mobile navigation preserves hidden state", /\.mobile-nav\[hidden\]\s*\{\s*display\s*:\s*none/.test(refinementCss) || /\.mobile-nav\[hidden\]\s*\{\s*display\s*:\s*none/.test(css)]);
checks.push(["Corporate sitemap includes all five pages", ["metatya.html", "company-ecosystem.html", "company-technology.html", "company-trust.html", "company-contact.html"].every(name => readFileSync("docs/sitemap.xml", "utf8").includes("/" + name))]);
for (const {path, html: pageHtml} of corporatePages) {
  const pageName = path.split("/").pop();
  const canonical = `https://maytyafx-debug.github.io/maytya/${pageName}`;
  checks.push([`${pageName} loads the corporate refinement stylesheet`, /<link rel="stylesheet" href="metatya-corporate-refinement\.css">/.test(pageHtml)]);
  checks.push([`${pageName} declares its canonical URL`, pageHtml.includes(`<link rel="canonical" href="${canonical}">`)]);
  checks.push([`${pageName} declares its Open Graph URL`, pageHtml.includes(`<meta property="og:url" content="${canonical}">`)]);
  checks.push([`${pageName} has a main landmark`, /<main\b[^>]*id="main"/.test(pageHtml)]);
}

const failed = checks.filter(([, ok]) => !ok);
for (const [name, ok] of checks) console.log(`${ok ? "PASS" : "FAIL"} ${name}`);
console.log(`\n${checks.length - failed.length}/${checks.length} checks passed`);
if (failed.length) process.exit(1);
