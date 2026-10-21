/* Keep the welcome banner visible, including browser back/forward restores. */
(() => {
  const messages = [
    "Welcome to my Website",
    "AI-augmented analytics for health, risk, and decision-making",
    "Health Metrics and the Spread of Infectious Diseases",
    "New book in progress: Mortality 🔍 Analytics - more info coming soon 🔥"
  ];
  let timer;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function start() {
    window.clearTimeout(timer);
    const banner = document.querySelector(".multipleStrings");
    if (!banner) return;
    banner.textContent = messages[0];
    if (reducedMotion.matches) return;
    let message = 0;
    let letters = Array.from(messages[0]);
    let position = letters.length;
    let deleting = true;

    function step() {
      if (!banner.isConnected) return;
      if (deleting && position > 1) {
        position -= 1;
      } else if (deleting) {
        message = (message + 1) % messages.length;
        letters = Array.from(messages[message]);
        position = 1;
        deleting = false;
      } else {
        position += 1;
      }
      // Retain at least one character so the banner never collapses to blank.
      banner.textContent = letters.slice(0, position).join("");
      if (!deleting && position === letters.length) {
        deleting = true;
        timer = window.setTimeout(step, 2400);
      } else {
        timer = window.setTimeout(step, deleting ? 30 : 45);
      }
    }
    timer = window.setTimeout(step, 2400);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
  window.addEventListener("pageshow", start);
  window.addEventListener("pagehide", () => window.clearTimeout(timer));
  reducedMotion.addEventListener("change", start);
})();
