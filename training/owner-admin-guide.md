# Owner practical guide

Prerequisites: Approved admin access, automation connections, queue read/recovery permissions, approval-center access and report refresh access.

Use synthetic development records only. All exercises and competency outcomes are Pending until an observer records tenant evidence. Replace .invalid identities before tenant execution. Read [lifecycle](../knowledge/01-order-lifecycle.md), [exceptions](../knowledge/02-approval-and-exceptions.md) and [artwork](../knowledge/03-artwork-and-quality.md).

## 10-minute walkthrough

Allocate two minutes to prerequisites/current record, six minutes to the numbered tasks and two minutes to result review. The facilitator prepares the required synthetic starting states.

1. **Inspect controls:** Verify AllowedRoles maps exact internal test identities. Test staff cannot edit Orders or submitted commands. Inspect connection ownership and enable flags before enabling flows. Expected outcome: Author-based authorization and authoritative-list protection are evidenced; role text never grants access.
2. **Reconcile uncertainty:** Inspect NeedsReview command/job/outbox with synthetic RequestKey ADMIN-DEMO-001. Compare current Orders, OrderEvents, approval center, Sent Items and Teams delivery evidence. Expected outcome: Document incident and proven effect before retry/reset. Never blindly recreate an approval or resend an uncertain message; preserve Status.
3. **Rehearse pause and refresh:** In development follow deployment/runbook.md to disable triggers/notifications and agent publication. Record outstanding ApprovalKeys. Refresh reporting and compare AsOfUtc and source counts. Expected outcome: History/files remain; stale cards are reconciled and report totals agree. Use rollout manual register during backout.

## Exception drill

Rehearse an approval creation with uncertain persistence. Identify possible existing approval in approval center and stop automatic retry. Record incident, evidence, decision and Owner signoff. Rehearse rollback without deleting lists/files.

Escalation: stop the affected step and contact Owner through the approved internal support route. Provide OrderKey, command ID, timestamp and redacted evidence. Owner involves admin for permissions/connections; unsupported business changes require a process decision. Never include secrets or customer artwork in a support prompt.

## Competency check

Observer records pass/fail, date and evidence for each item. All five must pass before independent pilot work.

- [ ] I can prove role and SharePoint permissions.
- [ ] I can identify owned healthy connections.
- [ ] I can reconcile uncertain effects before retry.
- [ ] I can pause flows and agent publication safely.
- [ ] I can preserve history and reconcile report refresh.

Observer: Pending. Exercise evidence: Pending. Result: Pending.
