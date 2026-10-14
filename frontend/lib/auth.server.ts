import "server-only";
import type { NextRequest } from "next/server";

const production = process.env.NODE_ENV === "production";
export const SESSION_COOKIE = production ? "__Host-aura_session" : "aura_session";
export const VERIFIER_COOKIE = production ? "__Host-aura_login_verifier" : "aura_login_verifier";
export const cookieOptions = { httpOnly: true, secure: production, sameSite: "lax" as const, path: "/" };

function origin(value: string): string {
  const url = new URL(value.includes("://") ? value : `https://${value}`);
  if (url.username || url.password || url.search || url.hash || url.pathname !== "/") {
    throw new Error("AURA server URLs must contain an origin only.");
  }
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if (url.protocol !== "https:" && !(local && url.protocol === "http:")) {
    throw new Error("AURA server URLs require HTTPS outside local development.");
  }
  return url.origin;
}

export function backendOrigin(): string {
  return origin(process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
}

export function frontendOrigin(request: NextRequest): string {
  // Render supplies the hostname. Pin redirects and CSRF checks to deployment
  // configuration instead of trusting a user-supplied forwarded Host header.
  return origin(process.env.FRONTEND_URL || process.env.RENDER_EXTERNAL_HOSTNAME || request.nextUrl.origin);
}

export const privateHeaders = { "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" };
