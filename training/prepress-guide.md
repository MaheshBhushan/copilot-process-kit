# Prepress practical guide

Prerequisites: Read Orders and DraftArtwork; approved file handling permissions; Add Items only in OrderCommands.

Use synthetic development records only. All exercises and competency outcomes are Pending until an observer records tenant evidence. Replace .invalid identities before tenant execution. Read [lifecycle](../knowledge/01-order-lifecycle.md), [exceptions](../knowledge/02-approval-and-exceptions.md) and [artwork](../knowledge/03-artwork-and-quality.md).

## 10-minute walkthrough

Allocate two minutes to prerequisites/current record, six minutes to the numbered tasks and two minutes to result review. The facilitator prepares the required synthetic starting states.

1. **Preflight:** Open the same-site DraftArtwork/demo-flyers.pdf, verify PDF <=20 MB and agreed bleed/fonts/page count. Record PreflightChecklistRef DEMO-PF-017. Expected outcome: Manual evidence identifies the exact draft; unsupported/missing files stop Validate.
2. **Validate:** On Submitted supply current ExpectedRevision, QuoteEUR 125.00, DraftFilePath, CustomerConsentRef DEMO-CONSENT-017, ApproverUPN approver@example.invalid and checklist reference. Replace identity with allowlisted test identity in tenant. Expected outcome: The dispatcher creates immutable ApprovalSnapshotPath before AwaitingApproval. Missing evidence requires RequestChanges with Reason.
3. **Release:** After Approved verify exact approved ApprovalKey and snapshot. Submit Release with current ExpectedRevision. Expected outcome: ReadyForProduction appears only after no-overwrite snapshot copy; PO-000123-r2-approved.pdf retains approval revision even when business Revision advances.

## Exception drill

Change the mutable draft after synthetic approval. Explain why Release must still use ApprovalSnapshotPath. For an artwork correction after Approved, stop and ask Owner for the supported correction/cancellation route.

Escalation: stop the affected step and contact Owner through the approved internal support route. Provide OrderKey, command ID, timestamp and redacted evidence. Owner involves admin for permissions/connections; unsupported business changes require a process decision. Never include secrets or customer artwork in a support prompt.

## Competency check

Observer records pass/fail, date and evidence for each item. All five must pass before independent pilot work.

- [ ] I can reject missing/external/non-PDF files.
- [ ] I can record manual preflight evidence.
- [ ] I can distinguish consent and approval.
- [ ] I can explain snapshot immutability.
- [ ] I can verify the released filename uses ApprovalKey revision.

Observer: Pending. Exercise evidence: Pending. Result: Pending.
