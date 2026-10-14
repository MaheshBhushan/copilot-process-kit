# Tenant evidence record

Status: **Pending — tenant execution unrun**. Copy this template into approved protected evidence storage for each test/recovery/release. Keep personal data, tokens and private URLs outside this repository. Replace Pending only with observed facts. A screenshot alone cannot prove authorization, idempotency or delivery.

| Field | Value |
|---|---|
| Record / acceptance case ID | Pending |
| Environment / tenant / site | Pending |
| Test authorization / licensing owner / decision date | Pending |
| Operator / tester / backup owner | Pending |
| UTC started / completed | Pending |
| Automation connection identity / actual flow version | Pending |
| EnableAutomation / EnableNotifications / active triggers | Pending |
| DLP policy / region / retention approval | Pending |
| Connection references / environment variables verified | Pending |
| Manual ALM fallback accepted, if applicable | Pending |
| Result / observed failure / limitation | Pending |
| Reviewer / pilot go-no-go / date | Pending |

## Connector binding probes

| Probe | Actual observed shape/settings | Redacted output/run link | Result |
|---|---|---|---|
| Immutable Author Email and Editor/version evidence | Pending | Pending | Pending |
| Choice normalization per list/action | Pending | Pending | Pending |
| ListItemEntityTypeFullName and ETag in GET response | Pending | Pending | Pending |
| Current ETag MERGE success and stale ETag 412 | Pending | Pending | Pending |
| Source/snapshot/release UniqueId, version, ETag and size | Pending | Pending | Pending |
| Deterministic Copy file name and no overwrite | Pending | Pending | Pending |
| Approval ID, actual outcome, responder UPN and ResponseAt | Pending | Pending | Pending |
| Approval notification option and reassignment disabled | Pending | Pending | Pending |
| Outlook/Teams success and actual provider reference if returned | Pending | Pending | Pending |
| Retry None on create/copy/send/post and claim MERGEs | Pending | Pending | Pending |
| Trigger/loop concurrency, pagination and 72h wait timeout | Pending | Pending | Pending |

## Per-case evidence

CaseID / Preconditions / exact Steps: Pending.

- Actual OrderKey and Orders item ID: Pending.
- Actual command ID, RequestKey, Author, ExpectedRevision and receipt version: Pending.
- Before/after Status, Revision, LastCommandKey and server timestamps: Pending.
- Actual EventKey, event row ID, CommandID and actor/role: Pending.
- Actual ApprovalKey, job ID, ApprovalId, assigned/responding UPN, ResponseAt and DeadlineUtc: Pending.
- Redacted actual flow run links and decisive action outputs, including retry/run-after evidence: Pending.
- Snapshot and release paths, source/destination UniqueId/version/ETag/size; ACL denial evidence: Pending.
- Actual outbox row IDs/keys, attempt count, received message link/ID or Sent Items evidence: Pending.
- Role-denial proof: attempted write identity, HTTP/action outcome and unchanged server row version: Pending.
- Queue/recovery proof: partial write point, automation receipt history, payload comparison and repair write versions: Pending.
- Tester, TestedAt UTC, reviewer, actual result and unresolved limitations: Pending.

An acceptance row can become Passed only after the actual tenant action and its expected invariant are observed. Failed and Blocked remain visible. Use NotApplicable only with a reviewed reason; never use it to bypass a required security case. Record all fixture changes, including accelerated deadlines, and distinguish them from real elapsed-time acceptance.

## Recovery decision

Incident ID/source state: Pending. Side effect certainty: Pending. Owner's observation and approval: Pending. Decision (complete missing deterministic writes / mark observed delivery / approved retry after conclusive nondelivery / preserve NeedsReview): Pending. Before/after versions and real operator: Pending. No business reversal, card recreation or resend is implied by this template.

## Local evidence boundary

Local CSV/JSON/link/action-map checks can prove document consistency. They cannot execute Power Automate, M or DAX; provision permissions; establish license entitlement; prove card response integrity, immutable copy semantics or message delivery. Local results belong in validation/local-report.md. Tenant results remain Pending until observed.
