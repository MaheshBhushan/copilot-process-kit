# Sales practical guide

Prerequisites: Read Orders; Add Items only in OrderCommands; DraftArtwork upload where approved. Customer consent evidence must be available.

Use synthetic development records only. All exercises and competency outcomes are Pending until an observer records tenant evidence. Replace .invalid identities before tenant execution. Read [lifecycle](../knowledge/01-order-lifecycle.md), [exceptions](../knowledge/02-approval-and-exceptions.md) and [artwork](../knowledge/03-artwork-and-quality.md).

## 10-minute walkthrough

Allocate two minutes to prerequisites/current record, six minutes to the numbered tasks and two minutes to result review. The facilitator prepares the required synthetic starting states.

1. **Submit:** Use RequestKey SALES-DEMO-001; Title Synthetic flyer run; CustomerCode DEMO-017; ProductType Flyers; Quantity 500; DueAt 2026-11-02T12:00:00Z. Submit once. Expected outcome: A new PO key has Submitted and Revision 1; check command outcome before repeating.
2. **Resubmit:** For a ChangesRequested or ApprovalExpired order, read current Revision. Set ExpectedRevision to it; provide updated business fields and Reason Corrected page count. Retain initial SubmittedAt. Expected outcome: Submitted has an incremented Revision; later Validate requires fresh approval.
3. **Cancel:** Choose only Submitted, ChangesRequested, ApprovalExpired, Approved or ReadyForProduction. Set current ExpectedRevision and Reason Synthetic customer withdrew. Expected outcome: Cancelled is terminal. AwaitingApproval and InProduction are excluded.

## Exception drill

Use a stale ExpectedRevision on a synthetic correction. Expect Rejected/StaleRevision without mutation. Read the latest row and discuss correction with Owner before a fresh command.

Escalation: stop the affected step and contact Owner through the approved internal support route. Provide OrderKey, command ID, timestamp and redacted evidence. Owner involves admin for permissions/connections; unsupported business changes require a process decision. Never include secrets or customer artwork in a support prompt.

## Competency check

Observer records pass/fail, date and evidence for each item. All five must pass before independent pilot work.

- [ ] I can distinguish CustomerConsentRef from internal approval.
- [ ] I can submit valid future UTC values.
- [ ] I can verify the command result without duplicate submission.
- [ ] I can resubmit with current ExpectedRevision and correction Reason.
- [ ] I can identify allowed cancellation states.

Observer: Pending. Exercise evidence: Pending. Result: Pending.
