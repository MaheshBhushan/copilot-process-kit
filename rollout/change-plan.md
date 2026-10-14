# Pilot change plan

All tenant activity, attendance, measurements and approvals are Pending. Owner is accountable; Sales champion coaches requirement/consent entry; Prepress champion coaches file/preflight/release practice; admin configures identities, permissions, connections, agent and reports. Approver and Production representatives observe their role exercises.

| Phase | Timing | Responsible | Evidence and exit |
|---|---|---|---|
| Baseline | Week 1 | Owner and Sales champion | Measure manual order lead time, missing fields, corrections, on-time completion and training confidence; record denominator and UTC period. Pending |
| Build/configure | Week 2 | Admin and Prepress champion | Native lists/flows configured disabled-first; source publication reviewed; permissions and acceptance run. Pending |
| Five-user pilot | Week 3 | Owner and champions | One internal learner per human guide; synthetic exercises before approved pilot data; daily incident review. Pending |
| Review | End week 3 | Owner | Reconcile results and resolve all gate failures; signed decision. Pending |
| Expand | Week 4 | Admin and champions | Add approved users up to 15 after role demonstrations; retain monitoring. Pending |
| Adoption check | Day 30 after pilot launch | Owner | Measure trained-user completion, authorized process use, corrections, lead time and source/report reliability against baseline. Pending |

## Go/no-go

Owner signs a dated evidence register before pilot publication and before expansion. Require 100% of security and process acceptance cases passed, 100% of critical assistant cases passed and all remaining assistant failures resolved or explicitly held from release; zero unresolved duplicate approvals; zero inaccessible production files for assigned users; five of five competency checks passed per pilot user; all uncertain-effect and rollback drills rehearsed; report counts and metrics reconciled with sources. Missing evidence is a hold. Adoption target at day 30 is at least 90% of eligible pilot orders using the authorized process and 100% of active users trained. Record counts and denominator. Owner decides corrective coaching if targets fail; no invented measured improvement.

Daily during pilot admin reviews NeedsReview and aged queues, source availability, connections and permissions. Champions review incomplete fields and coaching needs. Owner logs issue, severity, assignee, evidence and resolution date in the approved internal register. A leak, unauthorized mutation, duplicate approval or unavailable approved production file pauses affected work immediately.

## Backout and recovery

Owner declares backout and records timestamp/reason. Admin disables automation triggers and notifications using deployment/runbook.md and removes pilot agent publication/access. Admin preserves all lists, snapshots, released files, events, commands and evidence; no destructive reset. Owner reconciles outstanding ApprovalKeys against approval center and cancels stale cards where available. Record uncertain side effects before retrying anything. Never revive an expired approval.

Sales champion opens a controlled manual register in the approved internal SharePoint location with OrderKey, revision, status, quantity, due UTC, consent reference, internal approval reference/exact snapshot, released-file reference, QC, waste, operator, timestamp and incident reference. Preserve existing keys and histories. Sales records consent; Prepress verifies snapshot and release; Approver records the exact revision decision; Production verifies released artwork and QC. Owner controls manual changes and applies the same cancellation and terminal rules. Admin reconciles manual entries to native records with Owner signoff before re-enabling; do not bulk overwrite history or replay commands blindly. Rerun permission/process/security gates, notify users with the approved unsent draft and obtain Owner's dated restart decision.
