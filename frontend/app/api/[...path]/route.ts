import { NextRequest, NextResponse } from "next/server";
import { backendOrigin, cookieOptions, frontendOrigin, privateHeaders, SESSION_COOKIE } from "@/lib/auth.server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const allowedPaths = /^(?:auth\/(?:me|logout)|emails(?:\/\d+)?|calendar|tasks(?:\/\d+(?:\/plan)?)?|notes(?:\/\d+)?|memory(?:\/\d+)?|ask|dashboard\/(?:stats|briefing|sync)|actions(?:\/\d+\/(?:approve|reject))?|health)$/;
const maxBodyBytes = 1024 * 1024;

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const endpoint = path.join("/");
  if (!path.every(part => /^[A-Za-z0-9_-]+$/.test(part)) || !allowedPaths.test(endpoint)) {
    return NextResponse.json({ detail: "This API route does not exist." }, { status: 404, headers: privateHeaders });
  }
  const unsafe = !["GET", "HEAD"].includes(request.method);
  if (unsafe && (request.headers.get("origin") !== frontendOrigin(request)
      || request.headers.get("sec-fetch-site") === "cross-site")) {
    return NextResponse.json({ detail: "Please make this request from the AURA website." }, { status: 403, headers: privateHeaders });
  }
  const session = request.cookies.get(SESSION_COOKIE)?.value;
  if (endpoint !== "health" && (!session || !/^[A-Za-z0-9_-]{43}$/.test(session))) {
    return NextResponse.json({ detail: "Please sign in to AURA." }, { status: 401, headers: privateHeaders });
  }
  const headers: Record<string, string> = { Accept: "application/json, text/event-stream" };
  if (session) headers.Authorization = `Bearer ${session}`;

  let body: Uint8Array | undefined;
  if (unsafe && request.body) {
    // Bound memory use even when Content-Length is absent or inaccurate.
    const reader = request.body.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > maxBodyBytes) {
        await reader.cancel();
        return NextResponse.json({ detail: "This request is too large." }, { status: 413, headers: privateHeaders });
      }
      chunks.push(value);
    }
    if (size) {
      if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) {
        return NextResponse.json({ detail: "Use a JSON request body." }, { status: 415, headers: privateHeaders });
      }
      body = new Uint8Array(size);
      let offset = 0;
      for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
      headers["Content-Type"] = "application/json";
    }
  }

  try {
    const upstream = await fetch(`${backendOrigin()}/api/${endpoint}${request.nextUrl.search}`, {
      method: request.method, headers, body: body as BodyInit | undefined,
      cache: "no-store", redirect: "manual", signal: AbortSignal.timeout(120_000),
    });
    // The proxy is for data, never for forwarding login redirects or HTML pages.
    const contentType = upstream.headers.get("content-type") || "";
    if ((upstream.status >= 300 && upstream.status < 400)
        || (upstream.status !== 204 && !/^(application\/json|text\/event-stream)\b/.test(contentType))) {
      await upstream.body?.cancel();
      return NextResponse.json({ detail: "AURA could not reach its API. Please try again." }, { status: 502, headers: privateHeaders });
    }
    const response = new NextResponse(upstream.body, {
      status: upstream.status,
      headers: { ...privateHeaders, ...(contentType ? { "Content-Type": contentType } : {}) },
    });
    if ((endpoint === "auth/logout" && upstream.ok) || upstream.status === 401) {
      response.cookies.set(SESSION_COOKIE, "", { ...cookieOptions, maxAge: 0 });
    }
    return response;
  } catch {
    return NextResponse.json({ detail: "AURA is taking longer to respond. Please try again." }, { status: 503, headers: privateHeaders });
  }
}

export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE };
