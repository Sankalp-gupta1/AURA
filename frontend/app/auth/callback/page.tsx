"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function AuthCallbackPage() {
  const router = useRouter();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;
    const params = new URLSearchParams(window.location.hash.slice(1));
    const token = params.get("token");

    if (!token) {
      router.replace("/?error=oauth_failed");
      return;
    }

    window.localStorage.setItem("aura_token", token);
    window.history.replaceState(null, "", "/auth/callback");
    router.replace("/dashboard");
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="font-mono-ui text-sm text-[var(--color-muted)] animate-pulse">
        Signing you in to AURA…
      </p>
    </main>
  );
}
