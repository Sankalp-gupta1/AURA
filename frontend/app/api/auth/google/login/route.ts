import { createHash, randomBytes } from "node:crypto";
import { NextResponse } from "next/server";
import { backendOrigin, cookieOptions, privateHeaders, VERIFIER_COOKIE } from "@/lib/auth.server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const verifier = randomBytes(32).toString("base64url");
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  const url = new URL("/api/auth/google/login", backendOrigin());
  url.searchParams.set("challenge", challenge);
  const response = NextResponse.redirect(url, { status: 303, headers: privateHeaders });
  response.cookies.set(VERIFIER_COOKIE, verifier, { ...cookieOptions, maxAge: 600 });
  return response;
}
