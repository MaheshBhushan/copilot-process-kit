# Approver practical guide

Prerequisites: Assigned internal approval identity; read access to the exact snapshot and quote; native Approvals access.

Use synthetic development records only. All exercises and competency outcomes are Pending until an observer records tenant evidence. Replace .invalid identities before tenant execution. Read [lifecycle](../knowledge/01-order-lifecycle.md), [exceptions](../knowledge/02-approval-and-exceptions.md) and [artwork](../knowledge/03-artwork-and-quality.md).

## 10-minute walkthrough

Allocate two minutes to prerequisites/current record, six minutes to the numbered tasks and two minutes to result review. The facilitator prepares the required synthetic starting states.

1. **Inspect:** Open synthetic PO-000123-r2 card. Compare snapshot, Quantity 500, QuoteEUR 125.00 and consent reference to the request. Expected outcome: The assigned identity and exact revision are verified; a changed draft is irrelevant.
2. **Decide:** Before the 72 elapsed-hour deadline, approve or reject with clear rationale such as Page count differs from proof. Expected outcome: Automation checks ResponseUPN, ResponseAt <= DeadlineUtc and current AwaitingApproval/key/RequestedRevision. Approval becomes Approved; rejection becomes ChangesRequested.
3. **Check result:** Read authorized Orders after processing. Treat the 24-hour reminder as at most one per ApprovalKey. Expected outcome: A response at deadline can be processed later if guards still hold; internal approval does not release the file or replace consent.

## Exception drill

Open a synthetic stale card after ApprovalExpired. Do not act as if it authorizes production. Notify Owner to reconcile/cancel where available. No stale card or delayed decision revives applied expiry.

Escalation: stop the affected step and contact Owner through the approved internal support route. Provide OrderKey, command ID, timestamp and redacted evidence. Owner involves admin for permissions/connections; unsupported business changes require a process decision. Never include secrets or customer artwork in a support prompt.

## Competency check

Observer records pass/fail, date and evidence for each item. All five must pass before independent pilot work.

- [ ] I can identify exact ApprovalKey revision.
- [ ] I can inspect the immutable snapshot.
- [ ] I can give a useful decision rationale.
- [ ] I can explain elapsed-hour deadline equality.
- [ ] I can route stale cards to Owner.

Observer: Pending. Exercise evidence: Pending. Result: Pending.
