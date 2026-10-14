# AURA: Google Safe Browsing review notes

Updated October 14, 2026.

## What is still blocked

The owner verified `https://aura-backend-015h.onrender.com/` in Google Search
Console. Its Security Issues report showed **Deceptive pages**, with **Sample
URLs: N/A**. A Google security review has not been submitted by this release.
The warning's specific cause has not been established. Do not describe it as a
confirmed false positive or ask users to bypass it.

Google Safe Browsing review is separate from Google OAuth app verification.
Even after a browser warning is cleared, this app remains restricted to the
configured Google test users until its OAuth launch requirements are met.

## What changed

- Replaced the URL-fragment/localStorage login JWT with a Secure, HttpOnly,
  SameSite=Lax frontend session cookie. Browser JavaScript no longer reads the
  session credential. Legacy browser storage is cleared on page load.
- Added hashed, expiring server sessions. Logout revokes the current session.
  Old JWTs are no longer accepted. Existing users must sign in again.
- Added a two-minute, single-use, verifier-bound handoff between the Google
  callback and the frontend. A handoff code alone cannot sign someone in.
- Fixed Google PKCE: the verifier created at login is preserved for code exchange.
  Google authorization still uses `accounts.google.com`; token exchange uses
  `oauth2.googleapis.com`. The registered backend callback did not change.
- Routed browser data calls through same-origin frontend API routes. The server
  supplies the backend credential, rejects cross-site mutations, bounds request
  size, and only forwards explicitly allowed API paths.
- Added no-store and no-referrer responses, framing protection, and removal of
  OAuth query parameters from application access logs. Some provider failures
  now return generic messages instead of provider exception details.
- Updated vulnerable dependencies and removed unused authentication/form
  dependencies. PostCSS and source-map-js overrides keep patched versions under
  the existing Next.js major version.
- Added clear, independent AURA branding on the frontend and backend landing
  page. The backend homepage explains the API and links to AURA and its privacy
  policy. No password collection form or deceptive download was found in the
  reviewed application source.
- Preserved the public Search Console ownership file.

## Verification and its limits

Local verification for this release:

- Frontend production build and source lint passed.
- 21 backend checks passed, including account isolation, OAuth state, Google
  PKCE, session expiry/revocation, handoff replay rejection, encrypted Google
  token storage, and the exact public ownership file. The additional AI failure
  checks verify that provider errors are not returned or saved as chat answers,
  and that a failed briefing can recover on a later request.
- A separate production Next.js + FastAPI round-trip test passed with two
  synthetic accounts. It covers cookies, sign-in, private data, cross-site
  rejection, request size, streaming and logout.
- `pip-audit` on a fresh installed backend environment reported no known
  vulnerabilities. `npm audit --omit=dev` reported none for the frontend runtime
  dependency tree. These are dated dependency checks, not a security guarantee.

The tests use mocked Google/Gemini responses and temporary SQLite data. They do
not prove live Google consent, real Gmail/Calendar access, or Google's removal
of the warning. The hosting account, all historical deployments, and Google's
internal detection evidence have not been independently audited. No claim of a
complete infrastructure or malware audit is made.

The owner's October 14 screenshots also show an earlier successful Google sign-in,
an unapproved account being rejected with `403 access_denied`, and a Gemini model
availability error. The approved account can be selected in the Google account
chooser; other accounts need to be added as test users. The app default and Render
blueprint now use `gemini-3.8-flash`. The public health endpoint exposes only the
configured model name and deployment commit to help verify the running release;
these metadata do not prove that a live AI request succeeded.

## Review draft

Use this only after confirming both updated Render services are live. It is a
request to reassess the classification, not a statement that Google has approved
the site.

> I own https://aura-backend-015h.onrender.com/ and request a review of its
> “Deceptive pages” classification. Search Console shows Sample URLs: N/A, so I
> do not have a specific flagged page to investigate.
>
> AURA is an independent productivity application. Its frontend is
> https://aura-frontend-gmuw.onrender.com/ and this backend provides its API and
> Google OAuth callback. AURA does not collect Google passwords. Sign-in takes
> place on Google's official accounts.google.com service. The application uses
> read-only Gmail access and user-initiated or approved calendar actions.
>
> I reviewed the application code, public entry pages and OAuth redirects. I did
> not identify password collection forms or deceptive downloads in that source.
> The deployed update removes session tokens from URL fragments and browser
> storage, adds HttpOnly cookies and revocable sessions, preserves the Google
> PKCE verifier, rejects cross-site mutations, updates dependencies with known
> advisories, and clearly identifies AURA as an independent app with a privacy
> policy. Automated checks cover authentication and account isolation.
>
> These changes address issues found during the review; I have not established
> which, if any, triggered Google's classification. Please reassess the site,
> and provide an example URL if a deceptive page is still detected.

## Owner's next step

1. Open the verified backend property in Google Search Console.
2. Choose **Security & Manual Actions → Security issues**.
3. Select **REQUEST REVIEW** and use the draft above. Answer any additional
   questions according to what was actually inspected and changed.
4. Keep the submission confirmation. Do not say “review submitted” until it
   appears, and do not submit repeated requests while a review is pending.

Official guidance:

- https://developers.google.com/search/docs/monitor-debug/security/social-engineering
- https://support.google.com/webmasters/answer/9044101
- https://developers.google.com/identity/protocols/oauth2/web-server
