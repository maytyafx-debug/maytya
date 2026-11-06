/* =========================================================
   METATYA CONTENT BRIDGE
   File: docs/metatya-content-bridge.js
   Version: 1.0.0

   Purpose:
   Convert Metatya local admin exports into a versioned,
   validated content format.

   Safety:
   - Drafts are excluded by default.
   - Does not overwrite content.json.
   - Does not send data to external services.
   - Does not publish anything automatically.
========================================================= */

(function (global) {
  "use strict";

  const VERSION = "1.0.0";
  const OUTPUT_SCHEMA = "metatya-content-v1";
  const INPUT_SCHEMA = "metatya-local-content-draft";

  const CATEGORIES = [
    { id: "forex", name: "فارکس" },
    { id: "crypto", name: "ارزهای دیجیتال" },
    { id: "stocks", name: "بورس و سهام" },
    { id: "income", name: "درآمد و مهارت مالی" },
    { id: "business", name: "کسب‌وکار" },
    { id: "personal-finance", name: "مدیریت مالی شخصی" },
    { id: "education", name: "آموزش" },
    { id: "law", name: "حقوق و قوانین" },
    { id: "psychology", name: "روان‌شناسی" },
    { id: "ai", name: "هوش مصنوعی" },
    { id: "privacy", name: "حریم خصوصی" }
  ];

  const CATEGORY_IDS = new Set(
    CATEGORIES.map(category => category.id)
  );

  const ALLOWED_TYPES = new Set([
    "article",
    "guide",
    "lesson",
    "checklist",
    "news"
  ]);

  const ALLOWED_LEVELS = new Set([
    "beginner",
    "intermediate",
    "advanced",
    "general"
  ]);

  function isObject(value) {
    return (
      value !== null &&
      typeof value === "object" &&
      !Array.isArray(value)
    );
  }

  function cleanString(value, maxLength) {
    if (typeof value !== "string") return "";

    return value
      .replace(/\u0000/g, "")
      .trim()
      .slice(0, maxLength);
  }

  function makeId() {
    if (
      global.crypto &&
      typeof global.crypto.randomUUID === "function"
    ) {
      return global.crypto.randomUUID();
    }

    return (
      "metatya-" +
      Date.now().toString(36) +
      "-" +
      Math.random().toString(36).slice(2, 10)
    );
  }

  function normalizeTags(value) {
    if (!Array.isArray(value)) return [];

    return [...new Set(
      value
        .filter(tag => typeof tag === "string")
        .map(tag => cleanString(tag, 40))
        .filter(Boolean)
    )].slice(0, 20);
  }

  function normalizeItem(item, index) {
    if (!isObject(item)) {
      return {
        error: `مورد شماره ${index + 1} یک شیء معتبر نیست.`
      };
    }

    const title = cleanString(item.title, 120);

    if (!title) {
      return {
        error: `مورد شماره ${index + 1} عنوان ندارد.`
      };
    }

    const category = CATEGORY_IDS.has(item.category)
      ? item.category
      : null;

    if (!category) {
      return {
        error:
          `دسته‌بندی نامعتبر در مطلب «${title}»: ` +
          String(item.category || "خالی")
      };
    }

    const status =
      item.status === "published"
        ? "published"
        : "draft";

    const type = ALLOWED_TYPES.has(item.type)
      ? item.type
      : "article";

    const level = ALLOWED_LEVELS.has(item.level)
      ? item.level
      : "general";

    const now = new Date().toISOString();

    return {
      item: {
        id: cleanString(item.id, 100) || makeId(),
        title,
        category,
        type,
        level,
        status,
        summary: cleanString(item.summary, 500),
        body: cleanString(item.body, 30000),
        tags: normalizeTags(item.tags),
        createdAt:
          cleanString(item.createdAt, 40) || now,
        updatedAt:
          cleanString(item.updatedAt, 40) || now
      }
    };
  }

  function extractItems(input) {
    if (Array.isArray(input)) return input;

    if (!isObject(input)) {
      throw new Error("ساختار فایل ورودی معتبر نیست.");
    }

    if (Array.isArray(input.items)) {
      return input.items;
    }

    throw new Error(
      "فهرست مطالب در فایل ورودی پیدا نشد."
    );
  }

  function convert(input, options) {
    const settings = Object.assign(
      { includeDrafts: false },
      options || {}
    );

    const sourceItems = extractItems(input);

    const validItems = [];
    const errors = [];
    const seenIds = new Set();

    sourceItems.forEach((source, index) => {
      const result = normalizeItem(source, index);

      if (result.error) {
        errors.push(result.error);
        return;
      }

      const item = result.item;

      if (seenIds.has(item.id)) {
        errors.push(
          `شناسه تکراری در مطلب «${item.title}».`
        );
        return;
      }

      seenIds.add(item.id);

      if (
        settings.includeDrafts ||
        item.status === "published"
      ) {
        validItems.push(item);
      }
    });

    const output = {
      schema: OUTPUT_SCHEMA,
      version: 1,
      bridgeVersion: VERSION,
      generatedAt: new Date().toISOString(),
      publicationMode: settings.includeDrafts
        ? "preview-with-drafts"
        : "published-only",
      categories: CATEGORIES.map(category => ({
        id: category.id,
        name: category.name
      })),
      items: validItems
    };

    return {
      output,
      report: {
        inputCount: sourceItems.length,
        outputCount: validItems.length,
        excludedDrafts: sourceItems.filter(
          item =>
            isObject(item) &&
            item.status !== "published"
        ).length,
        errors,
        success: errors.length === 0
      }
    };
  }

  function validateOutput(data) {
    const errors = [];

    if (!isObject(data)) {
      return {
        valid: false,
        errors: ["خروجی یک شیء معتبر نیست."]
      };
    }

    if (data.schema !== OUTPUT_SCHEMA) {
      errors.push("شناسه schema معتبر نیست.");
    }

    if (data.version !== 1) {
      errors.push("نسخه ساختار پشتیبانی نمی‌شود.");
    }

    if (!Array.isArray(data.categories)) {
      errors.push("فهرست دسته‌بندی‌ها معتبر نیست.");
    }

    if (!Array.isArray(data.items)) {
      errors.push("فهرست مطالب معتبر نیست.");
    }

    if (errors.length) {
      return { valid: false, errors };
    }

    const ids = new Set();

    data.items.forEach((item, index) => {
      if (!isObject(item)) {
        errors.push(`مطلب شماره ${index + 1} معتبر نیست.`);
        return;
      }

      if (!item.id || !item.title) {
        errors.push(
          `مطلب شماره ${index + 1} شناسه یا عنوان ندارد.`
        );
      }

      if (ids.has(item.id)) {
        errors.push(`شناسه تکراری: ${item.id}`);
      }

      ids.add(item.id);

      if (!CATEGORY_IDS.has(item.category)) {
        errors.push(
          `دسته‌بندی نامعتبر برای ${item.title || item.id}`
        );
      }

      if (item.status !== "published") {
        errors.push(
          `مطلب غیرمنتشرشده در خروجی انتشار: ${item.title}`
        );
      }
    });

    return {
      valid: errors.length === 0,
      errors
    };
  }

  function createBlob(data) {
    const validation = validateOutput(data);

    if (!validation.valid) {
      throw new Error(
        "خروجی معتبر نیست: " +
        validation.errors.join(" | ")
      );
    }

    return new Blob(
      [JSON.stringify(data, null, 2)],
      { type: "application/json;charset=utf-8" }
    );
  }

  function download(data, filename) {
    if (!global.document || !global.URL) {
      throw new Error(
        "دانلود فقط در محیط مرورگر پشتیبانی می‌شود."
      );
    }

    const blob = createBlob(data);
    const url = global.URL.createObjectURL(blob);
    const link = global.document.createElement("a");

    link.href = url;
    link.download = filename || "metatya-content-v1.json";

    global.document.body.appendChild(link);
    link.click();
    link.remove();

    global.setTimeout(() => {
      global.URL.revokeObjectURL(url);
    }, 1000);
  }

  async function parseFile(file) {
    if (!file || typeof file.text !== "function") {
      throw new Error("فایل ورودی معتبر نیست.");
    }

    if (file.size > 5 * 1024 * 1024) {
      throw new Error(
        "حجم فایل بیشتر از حد مجاز ۵ مگابایت است."
      );
    }

    const text = await file.text();

    let parsed;

    try {
      parsed = JSON.parse(text);
    } catch {
      throw new Error("فایل JSON قابل خواندن نیست.");
    }

    if (
      isObject(parsed) &&
      parsed.schema &&
      parsed.schema !== INPUT_SCHEMA &&
      parsed.schema !== OUTPUT_SCHEMA
    ) {
      throw new Error("نوع فایل با این ابزار سازگار نیست.");
    }

    return parsed;
  }

  function audit(data) {
    const result = convert(data, { includeDrafts: true });
    const items = result.output.items;

    const categoryCounts = {};

    CATEGORIES.forEach(category => {
      categoryCounts[category.id] = 0;
    });

    items.forEach(item => {
      categoryCounts[item.category]++;
    });

    return {
      bridgeVersion: VERSION,
      generatedAt: new Date().toISOString(),
      total: result.report.inputCount,
      valid: items.length,
      invalid: result.report.errors.length,
      published: items.filter(
        item => item.status === "published"
      ).length,
      drafts: items.filter(
        item => item.status === "draft"
      ).length,
      categoryCounts,
      errors: result.report.errors
    };
  }

  const api = Object.freeze({
    version: VERSION,
    schema: OUTPUT_SCHEMA,
    categories: CATEGORIES,
    convert,
    validateOutput,
    createBlob,
    download,
    parseFile,
    audit
  });

  global.MetatyaContentBridge = api;

})(window);
