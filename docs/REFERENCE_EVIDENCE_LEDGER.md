# Reference Evidence Ledger

Updated: 2026-07-13  
Status: fixture-level reference evidence; product gate blocked

This ledger identifies the smallest reproducible public proof in this paused
repository. The inputs and reports were already committed at source revision
`7fa6ad2d2ec188c83b1e696f6ea232562811eac1`; this ledger adds exact checksums
and a machine-verifiable claim boundary without changing their contents.

## Evidence set

| Artifact | SHA-256 | What it establishes | What it does not establish |
|---|---|---|---|
| `tests/eval/fixtures/garage_door_leads.json` | `129f748ef6fd4253a7842620a9c2830ca767c18e80edb6e7751a418e7173a67a` | 50 synthetic scenarios and expected policy labels | Real leads, prevalence, user behavior, or label independence |
| `scripts/replay_demo_leads.py` | `010f7a124bd81cfa406cb9a1397c52b700a4d4e5e05881a64008e995473b0b04` | Deterministic artifact generator | Live providers, model quality, or production runtime |
| `docs/market/demo_replays/pre_pilot_replay_report.json` | `4b9d2a8652638ee8149b429d15ec76f50eaed6ab0d6831b2ae4e528e41deb89d` | 50/50 cases require human approval; zero fixture-policy autonomous sends | Autonomous-send safety in real traffic, ROI, conversion, or pilot readiness |
| `docs/market/demo_replays/baseline_comparison_report.json` | `07d601a87e393bd3bdaca55b11ae76c82adac61bc76b999b7024bc2a43dc5ea1` | Behavior of three deterministic, self-authored baseline modes | Comparative model performance or an independently designed benchmark |
| `docs/market/demo_replays/failure_mode_replay_report.json` | `361fc64a1e444d030fcacea25a3e145694d6868dc911c3c07c928379575f461b` | Seven injected failures route to review with no confirmed outbound send | Real provider failure rate, recovery, durability, or availability |

The machine-readable manifest is
`docs/evidence/reference_evidence_manifest.json`. Its unit test recomputes every
checksum and verifies the negative claims. The existing replay test rebuilds
the JSON artifacts semantically from the fixture.

## Reproduction

Run the five-minute path in the root README. `diff -qr` must produce no output,
then both tests must pass. The output directory is outside the repository so a
review does not overwrite committed evidence.

## Resume gate

Do not change the repository from paused/reference based on this evidence. A
resume decision needs a consented operator-owned lead flow, approved privacy
boundary, pre-intervention baseline, human decision/outcome records, and a new
evaluation plan that separates fixture conformance from real workflow quality.
No customer data or credentials should be requested merely to improve this
portfolio artifact.
