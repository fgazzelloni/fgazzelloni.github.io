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
    let message = 0;

    // Keep every message available without a character-by-character animation.
    // A longer pause also gives readers time to finish the longer messages.
    if (reducedMotion.matches) {
      function rotate() {
        if (!banner.isConnected) return;
        message = (message + 1) % messages.length;
        banner.textContent = messages[message];
        timer = window.setTimeout(rotate, 8000);
      }
      timer = window.setTimeout(rotate, 8000);
      return;
    }
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
  // Older Safari versions expose only the legacy MediaQueryList listener.
  if (typeof reducedMotion.addEventListener === "function") {
    reducedMotion.addEventListener("change", start);
  } else if (typeof reducedMotion.addListener === "function") {
    reducedMotion.addListener(start);
  }
})();
