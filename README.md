# Copilot Process Kit

**Local kit complete; tenant deployment Pending.** This package defines a Microsoft 365 print-shop pilot for 5–15 people. It includes reproducible synthetic data and local validation. It contains no deployed flows, saved PBIX, solution export or live agent results. Complete the tenant gates before enabling any automation.

Read the [detailed implementation handoff](.scratch/implementation-handoff.md) and [execution plan](.scratch/execution-plan.md) for architecture, contracts, task boundaries and verification gates.

## Quick start

Use Python 3.9+ with the standard library from this directory:

```sh
python3 scripts/generate_samples.py
python3 scripts/validate.py
```

Both scripts also work by absolute path from another working directory. The generator overwrites its six synthetic CSV/JSON outputs. The validator checks the saved determinism proof and writes [actual local results](validation/local-report.md). See [data notes](data/README.md) and [expected metrics](data/expected-metrics.json). Two recorded generator runs have identical hashes in [determinism evidence](validation/determinism.json).

Start with [the process guide](process/process-guide.md), [the readable diagram](process/print-order.svg) and [BPMN XML](process/print-order.bpmn). Build the local dashboard with [report setup](reporting/setup-guide.md). Follow [the deployment runbook](deployment/runbook.md) when an authorized tenant becomes available.

## Artifact classes

| Artifact | Purpose and status |
|---|---|
| [Process contract](contracts/process.json), [SharePoint schema](contracts/sharepoint-schema.json) | Versioned source contracts; local JSON and consistency checks |
| [Example environment](config/environment.example.json) | Disabled-first placeholders; no real tenant identifiers or credentials |
| [Provisioning guide](sharepoint/provisioning-guide.md), [permissions matrix](sharepoint/permissions-matrix.csv) | Manual setup instructions; actual access proof Pending |
| [Four flow guides](flows/README.md), [action map](flows/action-map.csv), [expressions](flows/expressions.md) | Native reconstruction instructions and field/action traceability; not importable cloud exports |
| [Deployment runbook](deployment/runbook.md), [35 acceptance cases](deployment/acceptance-cases.csv), [evidence template](deployment/evidence-template.md) | Deployment gates and observable proof requirements; all tenant cases Pending |
| [Agent setup](copilot/setup-guide.md), [instructions](copilot/agent-instructions.md), [28 evaluations](copilot/evaluation-cases.csv) | Authenticated read-only grounded agent specification; live responses Pending |
| [Lifecycle knowledge](knowledge/01-order-lifecycle.md), [approval knowledge](knowledge/02-approval-and-exceptions.md), [quality knowledge](knowledge/03-artwork-and-quality.md), [roles knowledge](knowledge/04-roles-and-service-levels.md) | Authoritative publishable source documents; use supported tenant formats per agent setup |
| [Sales](training/sales-guide.md), [Prepress](training/prepress-guide.md), [Approver](training/approver-guide.md), [Production](training/production-guide.md), [Owner/admin](training/owner-admin-guide.md), [prompt library](training/prompt-library.md) | Five role walkthroughs and 16 reviewed prompt templates |
| [Change plan](rollout/change-plan.md), [communications](rollout/communications.md) | Pilot rollout gates and unsent communication drafts |
| [Reporting setup](reporting/setup-guide.md), [dashboard layout](reporting/dashboard-layout.md) | Paste-ready M/DAX and manual Desktop steps; runtime/refresh/sharing Pending |
| [Synthetic data](data/README.md), [generator](scripts/generate_samples.py), [validator](scripts/validate.py) | 60 orders, 12 users, valid histories and separate synthetic usage; standard-library executable checks |
| [Manifest](manifest.json), [local report](validation/local-report.md) | Complete delivery inventory and observed local evidence |

## Tenant prerequisites and deployment hold

An authorized test tenant, verified service plans and licensing, an approved environment/DLP policy, pilot role identities, automation connections, site/list/library identifiers, permissions, retention, test mailbox/channel and human owners are required. Microsoft 365 E5 does not establish every Copilot Studio or Power BI entitlement. Read the runbook for exact gates and rollback. Keep automation and notifications disabled until the specified tests pass.

**File-copy gate:** the reconstruction currently requires the deprecated SharePoint **Copy file** action to supply an explicit deterministic destination filename and prohibit overwrite. If the action is unavailable or cannot meet those semantics, deployment stays **HOLD**. An approved replacement requires tenant tests before activation. The modern action must not be substituted silently.

SharePoint does not enforce per-column staff permissions. Staff submit commands; the dispatcher owns business state. ApprovalKey records the requested revision and remains unchanged after the decision increments the current revision. A response timestamp at the deadline can be accepted only while the matching request still awaits approval. Applied expiry cannot revive automatically. Uncertain technical effects require operator review; synthetic paths and scenario notes prove no actual file copy or delivery.

Local validation does not execute Power Query M, DAX, Power Automate, Copilot Studio, connector payloads or tenant permissions. Power BI Desktop build/reconciliation, 35 tenant acceptance cases, 28 agent evaluations and live adoption analytics remain Pending. No external message was sent and no tenant deployment was performed.
