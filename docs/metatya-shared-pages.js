(() => {
  "use strict";
  const root = document.documentElement;
  const menuButton = document.querySelector("[data-mt-menu-toggle]");
  const mobileMenu = document.querySelector("[data-mt-menu]");
  if (menuButton && mobileMenu) {
    menuButton.addEventListener("click", () => {
      const expanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!expanded));
      mobileMenu.hidden = expanded;
    });
    mobileMenu.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      menuButton.setAttribute("aria-expanded", "false");
      mobileMenu.hidden = true;
    }));
  }
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const revealItems = document.querySelectorAll("[data-mt-reveal]");
  if (!reduceMotion && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealItems.forEach(item => observer.observe(item));
  } else {
    revealItems.forEach(item => item.classList.add("is-visible"));
  }
  const year = document.querySelector("[data-mt-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
