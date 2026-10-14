# Synthetic sample data

All records use fixed AsOfUtc=2026-10-14T12:00:00Z and random.Random(42). These files contain no real people, customers, tenant IDs or artwork. Regeneration overwrites only the six generated CSV/JSON files listed below. The scripts resolve their own root and need Python 3.9+ with its standard library.

| File | Purpose |
|---|---|
| [Orders.csv](Orders.csv) | 60 current rows, exact Orders custom-field schema; blank nullable fields |
| [OrderEvents.csv](OrderEvents.csv) | 255 accepted transitions including Submit, every revision, exact OrderEvents schema |
| [Users.csv](Users.csv) | 12 pseudonymous eligible pilot users across five human roles |
| [Usage.csv](Usage.csv) | 147 independent synthetic measurement events; not a Microsoft analytics export |
| [scenarios.csv](scenarios.csv) | 60 order-linked scenario records covering 12 scenario types |
| [expected-metrics.json](expected-metrics.json) | Aggregations from serialized CSV facts, six-decimal rounding for ratios/hours |

Dates span nine weeks. Each scenario type has five orders: completed on time, completed late, administrative correction, rejection/resubmission, expired approval, cancellation, submitted backlog, awaiting approval, approved awaiting release, ready for production, in production and changes requested. The approved and ready scenarios include technical recovery drill notes. Those notes do not claim executed failures. Production QC rework stays within manual QC and does not create an invented transition.

OrderKey derives from the synthetic Submit CommandID. EventKey is OrderKey-rRevision. ApprovalKey records the requested revision and persists through that decision; it does not change to the Approved revision. Successful approval duration comes from the matching Validate event. Expired orders never revive. Final status/revision, timestamps and retained approval/release paths agree with the history. RequestKey is a required unique command field; this dataset contains Orders and OrderEvents, not a fabricated OrderCommands export.

Usage has EventID, EventAt, UserKey, Role, ActivityType and Outcome. AgentSession measures attempts across all outcomes. GuideViewed, TrainingCompleted and OrderCommand are independent demonstration activity records. Nine eligible users have successful training completions. No sessions or adoption values derive from Orders. Use [report setup](../reporting/setup-guide.md) for model filters, denominator definitions and the future governed analytics mapping.
