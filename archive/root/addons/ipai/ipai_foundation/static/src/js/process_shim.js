/**
 * Browser-safe shim for packages that expect Node-style `process`.
 * Keep minimal: enough to stop `process is not defined` from crashing OWL.
 */
(function () {
  if (typeof window !== "undefined" && typeof window.process === "undefined") {
    window.process = { env: {} };
  }
})();
