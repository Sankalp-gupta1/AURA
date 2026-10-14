"use client";

import { useEffect } from "react";

export default function SessionCleanup() {
  useEffect(() => {
    // One-time migration from older releases; sessions now use HttpOnly cookies.
    try { window.localStorage.removeItem("aura_token"); } catch { /* Storage can be disabled. */ }
    if (new URLSearchParams(window.location.hash.slice(1)).has("token")) {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }
  }, []);
  return null;
}
