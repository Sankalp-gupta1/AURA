import { NextRequest, NextResponse } from "next/server";
import { backendOrigin, cookieOptions, frontendOrigin, privateHeaders, SESSION_COOKIE, VERIFIER_COOKIE } from "@/lib/auth.server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code") || "";
  const verifier = request.cookies.get(VERIFIER_COOKIE)?.value || "";
  const destination = new URL("/?error=oauth_failed", frontendOrigin(request));
  // An explicit empty fragment also discards legacy token fragments on redirect.
  destination.hash = "#";
  let session: string | undefined;
  let expiresAt = 0;

  if (/^[A-Za-z0-9_-]{43}$/.test(code) && /^[A-Za-z0-9_-]{43}$/.test(verifier)) {
    try {
      const upstream = await fetch(`${backendOrigin()}/api/auth/session/exchange`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, verifier }), cache: "no-store", redirect: "error",
        signal: AbortSignal.timeout(120_000),
      });
      if (upstream.ok) {
        const payload = await upstream.json();
        if (typeof payload.session === "string" && /^[A-Za-z0-9_-]{43}$/.test(payload.session)
            && Number.isSafeInteger(payload.expires_at) && payload.expires_at > Date.now() / 1000) {
          session = payload.session;
          expiresAt = payload.expires_at;
          destination.pathname = "/dashboard";
          destination.search = "";
        }
      }
    } catch {
      // Never log the handoff code, verifier, session, or provider response.
      console.warn("AURA sign-in exchange could not be completed.");
    }
  }

  const response = NextResponse.redirect(destination, { status: 303, headers: privateHeaders });
  response.cookies.set(VERIFIER_COOKIE, "", { ...cookieOptions, maxAge: 0 });
  if (session) {
    response.cookies.set(SESSION_COOKIE, session, { ...cookieOptions, expires: new Date(expiresAt * 1000) });
  }
  return response;
}
