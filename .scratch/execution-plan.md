# Copilot Process Kit execution plan

## Assumptions

Build a local Microsoft 365 deployment kit for a 5–15 person print-shop pilot. Tenant credentials, licenses and deployment identifiers are unavailable. Local artifacts must be complete and checked; Microsoft deployment, Power BI execution and live agent evaluation remain Pending. Use native Microsoft products and Python standard library. No custom application, fake cloud exports, production data, external messages, commits or AI attribution.

## Overview

The implementation converts the architecture contract in [implementation-handoff.md](implementation-handoff.md) into a practical artifact package. The command queue protects authoritative SharePoint fields because SharePoint lacks column-level permissions. The outbox makes failed notifications recoverable without changing order decisions. These are ordinary lists and four native flows, not an application framework. For a pilot, manual reconciliation handles uncertain effects; no retry engine, distributed locks service or additional database belongs in scope.

## Task tree

```text
T1 Contracts, process, SharePoint setup
 ├─ T2 Flow reconstruction and deployment runbook
 └─ T3 Copilot knowledge, training and rollout
T1 + T2 + T3 → T4 Reporting, sample data, validation and final integration
```

Execute T1 first. T2 and T3 may run independently after the T1 gate, but they must not modify contracts. T4 follows both and produces final integration evidence. A worker can request a necessary contract correction from the owner; the orchestrator applies it and notifies affected workers. Do not let parallel workers silently rename fields.

## T1 — Stable contracts and process artifacts

- Model: `gpt-6.1-sol`; effort: medium. Contract consistency and BPMN require careful implementation.
- Dependencies: none.
- Inputs: architecture handoff sections 1–6 and 8.
- Output/blast radius: `config/`, `contracts/`, `process/`, `sharepoint/` only.
- Work: encode exact status/role/transition/schema contracts; add required unique RequestKey and immutable ApprovalSnapshotPath; provide environment placeholders; write manual provisioning and permission matrix; create real BPMN XML with complete DI and readable SVG; write process guide.
- Gate: JSON parsing succeeds; all table transitions appear in contract; every schema field has type/required/default/access metadata; stable BPMN IDs, references and DI resolve; diagram opens as SVG and has readable labels; authoritative lists deny staff edits in the documented matrix. Tenant permission proof remains Pending.
- Evidence: file paths, JSON parse command/result, XML structural command/result, native visual inspection of SVG if possible. Do not claim XSD validation unless run.

## T2 — Native flows and deployment

- Model: `gpt-6.1-sol`; effort: medium. Concurrency, approval uncertainty and recovery require exact mappings.
- Dependencies: T1 gate.
- Inputs: approved contracts, architecture sections 6–7 and 12–13.
- Output/blast radius: `flows/`, `deployment/` only.
- Work: write four action-by-action reconstruction guides, expression cookbook and action map. Include conditional ETag claim, immutable snapshot, 72h timeout, 24h reminder, deterministic effects, author-based role checks and manual uncertain-send recovery. Write disabled-first deployment sequence, licensing gates, rollback and at least 23 tenant acceptance cases.
- Gate: every business command has a flow path; each path cites exact contract fields and supported native action labels; every non-idempotent action has explicit retry/recovery instructions; approval wait never blocks dispatcher; deployment records contain Pending values rather than invented IDs; acceptance CSV has steps and observable evidence criteria.
- Evidence: contract/action cross-reference and CSV parsing; report actual tenant tests as unrun.

## T3 — Grounded assistant and people enablement

- Model: `gpt-6.1-sol`; effort: low. This task applies an already-fixed process to documents.
- Dependencies: T1 gate.
- Inputs: approved contracts, process guide, architecture sections 9–10.
- Output/blast radius: `copilot/`, `knowledge/`, `training/`, `rollout/` only.
- Work: four authoritative grounding guides; authenticated SharePoint setup; no-write agent instructions; 20+ evaluation cases; five role guides; 15+ usable prompt templates with synthetic examples; rollout plan, competency checks and unsent communications. Provide supported-format publishing guidance for Markdown sources.
- Gate: lifecycle and timing terms match contract; every role has a walkthrough and exception drill; every prompt distinguishes facts from generated text and includes human review; critical access/prompt-injection/action tests exist; all live results are Pending; rollout has measurable go/no-go and rollback responsibilities.
- Evidence: counts and content cross-check; no claimed live assistant responses.

## T4 — Data, reporting, validation and integration

- Model: `gpt-6.1-sol`; effort: medium. Cross-artifact checks and metric reconciliation require executable precision.
- Dependencies: T1, T2 and T3 gates.
- Inputs: all approved artifacts and architecture sections 11–14.
- Output/blast radius: `README.md`, `manifest.json`, `reporting/`, `data/`, `scripts/`, `validation/`, optional kit-local `.gitignore`. May fix integration issues in earlier outputs only after coordinating ownership; never change `.scratch/` architect files.
- Work: deterministic 60-order, 12-user dataset with valid histories; separate synthetic usage; scenarios and expected metrics; paste-ready local/SharePoint M, DAX and model/layout guide; standard-library generator and validator; manifest and quick start. Run checks and record actual outcomes.
- Gate: generator runs from any working directory; two runs have identical data hashes; validator exits 0 and prints meaningful checks; sample histories cover all states and reconcile with current rows; metrics reconcile with CSV; manifest files and Markdown links resolve; no fake export files; all live acceptance entries remain Pending.
- Evidence commands from kit root:

```sh
python3 scripts/generate_samples.py
python3 scripts/validate.py
```

Compute SHA256 for generated CSV/JSON files with Python before and after regeneration. Record actual counts, hashes and checks in `validation/local-report.md`. Static string presence cannot prove M/DAX runtime correctness; document Desktop execution as Pending.

## Worker brief rules

Each worker receives only its task description, relevant inputs, blast radius, gate and these rules:

> Touch only what you must. Every changed line must trace directly to this subtask. Do not improve adjacent code, comments, or formatting. Do not refactor what isn't broken. Match the existing style even if you'd write it differently. If you notice unrelated dead code, report it in your summary — do not delete it. Do remove imports, variables and functions that your changes orphaned.

You are not alone in the codebase. Preserve others' work. Ask the orchestrator to coordinate contract changes. Do not commit, publish, send external messages, or add AI attribution. Return files, exact gate results, commands and limitations.

## Final release gate

Orchestrator independently runs the validator, inspects representative BPMN/training/flow/report artifacts, and checks Git diff scope. Deliver one concise local-completion statement, artifact link and exact tenant prerequisites. Do not describe tenant deployment as complete. User authorization already covers implementation; no additional planning approval is required.
