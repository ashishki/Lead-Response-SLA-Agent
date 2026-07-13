# Security policy

Lead Response SLA Agent is a paused, local reference implementation, not a
hosted product. Reports are accepted only for the current default branch or the
identified `reference-v0.1.0` boundary and its documented fixture, fake-provider,
PostgreSQL/Redis integration, RLS, approval, and no-send contracts. No production
deployment, customer workflow, supported provider account, or security SLA is
claimed.

Do not open a public issue for a suspected vulnerability. Email
`verter25@gmail.com` with subject `Lead-Response-SLA-Agent security report`.
Include the exact revision, prerequisites, a minimal synthetic reproduction,
impact, and suggested mitigation. Keep the first message minimal. Do not attach
real leads, contact details, tenant exports, provider payloads, credentials,
tokens, `.env` files, private URLs, database content, or an exploit against a
system or data you do not own. A safer detail-transfer path can be agreed before
sending sensitive material.

GitHub private vulnerability reporting is not assumed to be enabled. Use a
GitHub private advisory form only if the repository Security page visibly
offers **Report a vulnerability**. This paused maintainer-run reference cannot
promise a response or remediation deadline.

If a credential or private record is exposed, stop publication and rotate or
revoke the credential at its provider. Removing a later commit does not retract
copies already fetched.
