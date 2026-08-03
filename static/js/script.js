window.addEventListener("DOMContentLoaded", () => {
  const nav = document.querySelector(".custom-nav");
  const syncNavigation = () => nav?.classList.toggle("is-scrolled", window.scrollY > 24);
  syncNavigation();
  window.addEventListener("scroll", syncNavigation, { passive: true });

  const themeButton = document.getElementById("themeBtn");
  if (themeButton) {
    themeButton.addEventListener("click", () => document.body.classList.toggle("dark"));
  }

  document.querySelectorAll(".counter").forEach((counter) => {
    const target = Number(counter.dataset.target || 0);
    const duration = 900;
    const start = performance.now();
    const update = (time) => {
      const progress = Math.min((time - start) / duration, 1);
      counter.textContent = `${Math.round(target * progress)}${progress === 1 ? "+" : ""}`;
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  });

  const cards = document.querySelectorAll(".csv-job-card, .dashboard-card, .status-card");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    cards.forEach((card, index) => {
      card.style.setProperty("--reveal-delay", `${Math.min(index % 8, 5) * 45}ms`);
      card.classList.add("reveal-card");
      observer.observe(card);
    });
  }

  document.querySelectorAll(".job-filter-card").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type='submit']");
      if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Filtering';
      }
    });
  });
});
