# AURA: open signup with Google

Prepared October 14, 2026 against application release `7fab2b6`.

## The intended experience

A person opens AURA, signs in with their own Google account, reviews the requested
permissions, and gets a private workspace. The owner does not add each person's
email address to a test-user list. Each person must still consent to access to
their own Gmail and Calendar; publishing cannot remove that consent requirement.

The backend already creates a separate user record from the verified Google
identity. `backend/app/api/auth.py` contains no owner-email allowlist. The
reported `403 access_denied` is from Google's testing configuration.

## Publishing and approval are different

| Google setting | What it means for signup |
| --- | --- |
| External / Testing | Only listed test users can authorize this app's Gmail/Calendar request. |
| External / In production, scopes unverified | The manual tester list is no longer the entry gate, but unverified warnings and Google's user cap still apply. The standard cap is 100 new users, with Google able to adjust it. |
| External / In production, required scopes approved | Eligible accounts can authorize without the owner adding them. Organization account policies, API quotas and service availability can still limit access. |

Do not label the app fully public merely because **Publish app** was clicked.
The existing Chrome Safe Browsing issue also needs its separate Search Console
review; OAuth approval does not automatically clear a browser warning.

## Settings to keep

| Field | Value |
| --- | --- |
| Cloud project | `aura-505303` |
| User type | External |
| App name | AURA |
| Homepage | `https://aura-frontend-gmuw.onrender.com/` |
| Privacy policy | `https://aura-frontend-gmuw.onrender.com/privacy` |
| Production JavaScript origin | `https://aura-frontend-gmuw.onrender.com` |
| Production redirect URI | `https://aura-backend-015h.onrender.com/api/auth/google/callback` |

Keep the existing client and secrets. Changing the audience does not require a
new client secret or a different callback. Keep unrelated Cloud resources intact.

## Draft app description

AURA is an independent personal productivity application. Users connect their
own Google account to view recent inbox messages and upcoming calendar events in
a private dashboard. Selected context supports email summaries, suggested tasks,
briefings and answers to the user's questions. Calendar features list upcoming
events and create events in the user's primary calendar. AURA does not collect
Google passwords; Google handles sign-in and consent.

## Scopes: current code and review preparation

| Scope | Current purpose and review note |
| --- | --- |
| `openid` | Establish a Google identity for the account. |
| `https://www.googleapis.com/auth/userinfo.email` | Identify the signed-in account and show its email. |
| `https://www.googleapis.com/auth/userinfo.profile` | Show the person's name and profile image. |
| `https://www.googleapis.com/auth/gmail.readonly` | Read recent inbox messages for the inbox view, summaries and task extraction. The implementation fetches message content; label-only permissions cannot support that behavior. This is a restricted scope. |
| `https://www.googleapis.com/auth/calendar` | Currently used for event listing and creation. This is broader than those operations require. Before submitting, evaluate a narrower event scope against both API calls and update code, declared scopes and the demo together. Do not claim full-calendar management is necessary. |

Do not replace Gmail reading with `gmail.send` or label-only access just to avoid
review: those scopes cannot implement the current inbox features.

## Readiness gaps to resolve before inviting the public

1. **Restricted-scope review and assessment.** This implementation reads Gmail on
   a server, stores synchronized data and sends selected context to Gemini.
   Google's restricted-scope process therefore applies, including the security
   assessment requirement unless Google confirms an applicable exception.
   A public launch is not the personal-use exception. Do not purchase an
   assessment or enable billing without the owner's approval.
2. **AI data handling.** The live key's billing/data-processing status has not been
   verified. Google's unpaid Gemini terms permit product/model improvement and
   say not to submit sensitive, confidential or personal information. Workspace
   policy prohibits using this data to improve models beyond the permitted
   personalized use. Confirm an appropriate processing arrangement before
   sending real inbox data to AI; do not assume a working key proves compliance.
   Paid-service terms differ, but billing must be an explicit owner decision.
3. **Privacy and user control.** The current privacy page describes access,
   storage and Gemini processing. It still needs an accurate retention/deletion
   process and a support contact. Google-access revocation stops new access; it
   does not itself delete already stored AURA data. Do not promise a deletion
   feature that the application has not implemented and verified.
4. **Domains and browser reputation.** Verify the domains required by Google's
   review. The existing backend verification file does not prove ownership of
   every frontend domain. Resolve the reported Safe Browsing issue using
   [the prepared security review notes](SECURITY_REVIEW.md).
5. **Real acceptance evidence.** Record a successful consent, sync and AI response
   using controlled test data. Existing automated checks mock Google/Gemini;
   they do not replace this recording or independent assessment.
6. **Operations.** Confirm persistent database lifetime, recovery and expected
   traffic capacity. Free hosting and AI quotas do not promise unlimited usage.

## Owner's Console steps

1. Open Google Cloud Console and select **AURA / aura-505303**.
2. Open **Google Auth Platform → Audience**. Keep **External**. Review the
   **Publishing status**. When ready to request production verification, select
   **Publish app** and read its confirmation. This alone is not approval.
3. Under **Branding**, check the homepage, privacy URL, support/developer contact
   and required domain ownership. Complete branding verification/publishing as
   prompted by the current Console.
4. Under **Data access**, declare only the scopes actually used by the final code.
5. In **Verification Center**, prepare the data-access submission with accurate
   scope justifications and a real demo video. Resolve the gaps above before
   certifying that the app meets the requirements.
6. Submit only accurate statements and keep Google's confirmation. Follow the
   review team's assessment instructions and any later recertification requests.

The Console was unavailable from the assistant's browser during this check.
No publishing status, scope declaration, billing setting or review submission
was changed by preparing this document.

## Demo video outline

Use a controlled account with non-sensitive test messages/events. Show the public
homepage and privacy link; the Google consent flow in English with AURA's identity
and client ID visible; inbox synchronization; the actual Gmail-derived feature;
calendar listing and a test event created with the account owner's approval;
the data-control flow after it is implemented; and logout. Hide secrets and
unrelated personal content. Use an unlisted video when submitting the review.
Do not present sample-data screens as proof that real Google integration works.

## Official references

- [Audience, production status and user caps](https://support.google.com/cloud/answer/15549945)
- [Restricted-scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification)
- [Gmail scope classification](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Submitting for verification](https://support.google.com/cloud/answer/13461325)
- [Workspace data-use policy](https://developers.google.com/workspace/workspace-api-user-data-developer-policy)
- [Gemini API terms](https://ai.google.dev/gemini-api/terms)
