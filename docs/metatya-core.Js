(() => {
  "use strict";

  const Metatya = {
    version: "1.0.0",

    init() {
      this.initReveal();
      this.initMobileMenu();
      this.initTabs();
      this.initAccordions();
      this.initSmoothScroll();
      this.initYear();
      this.initForms();
    },

    initReveal() {
      const elements = document.querySelectorAll(".mt-reveal");

      if (!("IntersectionObserver" in window)) {
        elements.forEach(element => element.classList.add("is-visible"));
        return;
      }

      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 });

      elements.forEach(element => observer.observe(element));
    },

    initMobileMenu() {
      const toggle = document.querySelector("[data-mt-menu-toggle]");
      const menu = document.querySelector("[data-mt-menu]");

      if (!toggle || !menu) return;

      toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";

        toggle.setAttribute("aria-expanded", String(!expanded));
        menu.hidden = expanded;
      });

      menu.querySelectorAll("a").forEach(link => {
        link.addEventListener("click", () => {
          menu.hidden = true;
          toggle.setAttribute("aria-expanded", "false");
        });
      });
    },

    initTabs() {
      document.querySelectorAll("[data-mt-tabs]").forEach(group => {
        const buttons = [...group.querySelectorAll("[data-mt-tab]")];
        const panels = [...group.querySelectorAll("[data-mt-panel]")];

        const activate = id => {
          buttons.forEach(button => {
            const active = button.dataset.mtTab === id;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
          });

          panels.forEach(panel => {
            const active = panel.dataset.mtPanel === id;
            panel.hidden = !active;
          });
        };

        buttons.forEach(button => {
          button.addEventListener("click", () => activate(button.dataset.mtTab));
        });

        if (buttons.length) activate(buttons[0].dataset.mtTab);
      });
    },

    initAccordions() {
      document.querySelectorAll("[data-mt-accordion]").forEach(group => {
        const items = [...group.querySelectorAll("[data-mt-accordion-item]")];

        items.forEach(item => {
          const button = item.querySelector("[data-mt-accordion-trigger]");
          const panel = item.querySelector("[data-mt-accordion-panel]");

          if (!button || !panel) return;

          button.addEventListener("click", () => {
            const isOpen = button.getAttribute("aria-expanded") === "true";

            button.setAttribute("aria-expanded", String(!isOpen));
            panel.hidden = isOpen;
            item.classList.toggle("is-open", !isOpen);
          });
        });
      });
    },

    initSmoothScroll() {
      document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", event => {
          const target = document.querySelector(link.getAttribute("href"));

          if (!target) return;

          event.preventDefault();
          target.scrollIntoView({
            behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
              ? "auto"
              : "smooth",
            block: "start"
          });
        });
      });
    },

    initYear() {
      document.querySelectorAll("[data-mt-year]").forEach(element => {
        element.textContent = new Date().getFullYear();
      });
    },

    initForms() {
      document.querySelectorAll("[data-mt-form]").forEach(form => {
        form.addEventListener("submit", event => {
          if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
          }

          const status = form.querySelector("[data-mt-status]");

          if (status) {
            status.textContent = "اطلاعات آماده ارسال است.";
          }
        });
      });
    },

    notify(message, type = "success") {
      let container = document.querySelector("[data-mt-notifications]");

      if (!container) {
        container = document.createElement("div");
        container.dataset.mtNotifications = "";
        container.setAttribute("aria-live", "polite");
        container.style.cssText =
          "position:fixed;bottom:20px;right:20px;z-index:9999;display:grid;gap:10px";
        document.body.appendChild(container);
      }

      const notification = document.createElement("div");
      notification.textContent = String(message);
      notification.setAttribute("role", "status");
      notification.style.cssText = `
        max-width:min(90vw,380px);
        padding:14px 20px;
        border:1px solid ${type === "error" ? "#ff5263" : "#00ff9d"};
        border-radius:12px;
        background:#0b1210;
        color:#f2f7f4;
        box-shadow:0 10px 35px rgba(0,0,0,.35);
      `;

      container.appendChild(notification);

      window.setTimeout(() => notification.remove(), 4000);
    }
  };

  window.Metatya = Metatya;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => Metatya.init(), { once: true });
  } else {
    Metatya.init();
  }
})();
