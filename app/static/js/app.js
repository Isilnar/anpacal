"use strict";

/**
 * PWA app.js — suppresses the default mini-infobar on mobile.
 * Installation is handled natively by the browser UI (address bar icon / menu).
 */
(function () {
  // Prevent the mini-infobar from appearing on mobile
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
  });
})();
