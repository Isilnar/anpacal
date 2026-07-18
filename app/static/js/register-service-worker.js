"use strict";

/**
 * Register the service worker for PWA offline support.
 * Called from layout.html when IS_PWA=1.
 */
function registerServiceWorker(swUrl) {
  if (!("serviceWorker" in navigator)) {
    console.log("Service Workers not supported in this browser.");
    return;
  }

  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register(swUrl)
      .then((registration) => {
        console.log("SW registered, scope:", registration.scope);
      })
      .catch((err) => {
        console.error("SW registration failed:", err);
      });
  });
}
