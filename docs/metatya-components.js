(() => {
  "use strict";

  const Data = window.MetatyaData;

  if (!Data) {
    console.error("MetatyaData بارگذاری نشده است.");
    return;
  }

  const escapeHTML = value =>
    String(value ?? "").replace(/[&<>"']/g, char => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[char]);

  const Components = {
    pillarCard(item) {
      return `
        <article class="mt-card mt-reveal" data-pillar="${escapeHTML(item.id)}">
          <div class="mt-card-icon">${escapeHTML(item.icon)}</div>
          <h3>${escapeHTML(item.title)}</h3>
          <p>${escapeHTML(item.description)}</p>
          <div class="mt-card-meta">
            ${item.tracks.map(track =>
              `<span class="mt-chip">${escapeHTML(track)}</span>`
            ).join("")}
          </div>
          <a class="mt-card-link"
             href="pillar.html?id=${encodeURIComponent(item.id)}">
             مشاهده مسیر آموزشی ←
          </a>
        </article>
      `;
    },

    productCard(item) {
      return `
        <article class="mt-card mt-product mt-reveal"
                 data-product="${escapeHTML(item.id)}">
          <span class="mt-product-tag">${escapeHTML(item.level)}</span>
          <h3>${escapeHTML(item.title)}</h3>
          <p>${escapeHTML(item.description)}</p>
          <ul class="mt-feature-list">
            ${item.features.map(feature =>
              `<li>${escapeHTML(feature)}</li>`
            ).join("")}
          </ul>
          <a class="mt-button mt-button-outline"
             href="${escapeHTML(item.url)}"
             target="_blank"
             rel="noopener noreferrer">
             ${escapeHTML(item.action)}
          </a>
        </article>
      `;
    },

    fitCard(item) {
      return `
        <article class="mt-card mt-reveal"
                 data-fit-track="${escapeHTML(item.id)}">
          <div class="mt-card-icon">🏅</div>
          <h3>${escapeHTML(item.title)}</h3>
          <p>${escapeHTML(item.description)}</p>
          <p class="mt-fit-audience">
            مخاطب: ${escapeHTML(item.audience)}
          </p>
          <ul class="mt-feature-list">
            ${item.modules.map(module =>
              `<li>${escapeHTML(module)}</li>`
            ).join("")}
          </ul>
        </article>
      `;
    },

    render(selector, items, renderer) {
      const target = document.querySelector(selector);
      if (!target) return false;

      target.innerHTML = items.map(renderer).join("");

      if (window.Metatya) {
        window.Metatya.initReveal();
      }

      return true;
    },

    renderPillars(selector = "[data-mt-pillars]") {
      return this.render(
        selector,
        Data.pillars,
        item => this.pillarCard(item)
      );
    },

    renderProducts(selector = "[data-mt-products]") {
      return this.render(
        selector,
        Data.products,
        item => this.productCard(item)
      );
    },

    renderFit(selector = "[data-mt-fit]") {
      return this.render(
        selector,
        Data.fitTracks,
        item => this.fitCard(item)
      );
    },

    renderAll() {
      this.renderPillars();
      this.renderProducts();
      this.renderFit();
    }
  };

  window.MetatyaComponents = Components;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      Components.renderAll();
    }, { once: true });
  } else {
    Components.renderAll();
  }
})();
