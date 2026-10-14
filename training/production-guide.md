# Production practical guide

Prerequisites: Read released ProductionFiles and Orders; configured Production identity; Add Items only in OrderCommands.

Use synthetic development records only. All exercises and competency outcomes are Pending until an observer records tenant evidence. Replace .invalid identities before tenant execution. Read [lifecycle](../knowledge/01-order-lifecycle.md), [exceptions](../knowledge/02-approval-and-exceptions.md) and [artwork](../knowledge/03-artwork-and-quality.md).

## 10-minute walkthrough

Allocate two minutes to prerequisites/current record, six minutes to the numbered tasks and two minutes to result review. The facilitator prepares the required synthetic starting states.

1. **StartProduction:** On ReadyForProduction open ReleasedFilePath PO-000123-r2-approved.pdf. Submit current ExpectedRevision and configured ProductionUPN. Expected outcome: InProduction appears only if the released file exists and identity is authorized.
2. **QC and rework:** Check synthetic job quantity 500 against agreed quality specification. Record defects, rework, then repeat manual QC. Expected outcome: Status remains InProduction during rework; no bypass or extra QC state is invented.
3. **Complete:** After QC passes submit current ExpectedRevision, QCReference DEMO-QC-017 and WasteQuantity 5. Expected outcome: Completed records dispatcher timestamp; waste is integer 0..Quantity. Completed is terminal.

## Exception drill

Attempt to locate a missing released PDF. Stop before StartProduction and escalate to Owner. For cancellation after start, record the concern and request Owner review without submitting an unsupported Cancel.

Escalation: stop the affected step and contact Owner through the approved internal support route. Provide OrderKey, command ID, timestamp and redacted evidence. Owner involves admin for permissions/connections; unsupported business changes require a process decision. Never include secrets or customer artwork in a support prompt.

## Competency check

Observer records pass/fail, date and evidence for each item. All five must pass before independent pilot work.

- [ ] I can identify the released snapshot filename.
- [ ] I can verify file access before starting.
- [ ] I can submit the assigned ProductionUPN.
- [ ] I can repeat QC after rework.
- [ ] I can provide valid QCReference and waste.

Observer: Pending. Exercise evidence: Pending. Result: Pending.
