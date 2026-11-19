(() => {
  "use strict";
  const button = document.querySelector(".menu-toggle");
  const menu = document.querySelector(".mobile-nav");
  if (button && menu) {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      menu.hidden = expanded;
    });
    menu.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      button.setAttribute("aria-expanded", "false");
      menu.hidden = true;
    }));
  }
  const year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();