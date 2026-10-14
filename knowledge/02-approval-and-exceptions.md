# Approval and exceptions

Authority: process contract 1.0. Owner approves changes before republication.

Sales records external customer consent as CustomerConsentRef through ordinary business communication. Internal Approver authorization is separate. Every order requires internal approval; no price threshold removes it. Consent alone does not authorize production, and internal approval does not prove customer consent.

Validate creates an immutable ApprovalSnapshotPath before changing status. ApprovalKey contains the revision on entry to AwaitingApproval, for example PO-000123-r2. ApprovalJobs.RequestedRevision identifies that revision. The internal approval references exact quantity, QuoteEUR, consent reference and snapshot.

ApprovalDueAt and DeadlineUtc represent 72 elapsed hours after request creation in UTC. There is no business-calendar pause. At most one reminder is sent per ApprovalKey after 24 hours and before the deadline. Approver checks identity, snapshot and rationale before responding. ResponseAt must be less than or equal to DeadlineUtc. A response recorded at the deadline can be accepted even if processed later, provided the current state remains AwaitingApproval and ApprovalKey, RequestedRevision and assigned ResponseUPN match. An applied expiry or changed revision rejects the queued decision. No late card or delayed command can revive expired work. Owner investigates queue ordering without automatic revival.

Rejection retains Reason and moves to ChangesRequested. Expiry moves to ApprovalExpired. Sales corrects and Resubmits; a new Validate creates a new approval revision. Never reuse the expired approval. Stale cards may remain visible; Owner reconciles/cancels them in the approval center where available. Do not assume a flow timeout cancels a card.

If approval creation or a notification has an uncertain result, Owner checks the approval center, Sent Items or Teams evidence before any retry. Never create a replacement approval blindly. A notification failure never rolls back an order. NeedsReview records technical incidents separately from business status. Missing permissions, inaccessible snapshots and conflicting revisions go to Owner.
