# Roles and service levels

Authority: process contract 1.0. Owner approves changes before republication.

Sales records customer requirements and consent evidence, submits, corrects/resubmits and requests permitted cancellation. Prepress validates the quote and PDF, records preflight, requests changes and releases approved snapshots. Approver decides on the assigned exact revision with a rationale. Production starts assigned released work, performs QC/rework and completes it. Owner manages exceptions, recovery and rollout. Automation processes authorized commands and approval outcomes. The five human role guides give practical exercises.

Authorization uses immutable OrderCommands.Author and the administrator's exact AllowedRoles UPN mapping. A typed role or email cannot grant access. Staff read Orders and add commands but cannot edit/delete submitted commands or authoritative Orders, ApprovalJobs, OrderEvents and Outbox. Administrators maintain permissions and automation connections. Hidden form columns do not secure data.

Store dates in UTC ISO 8601 with Z. Approval timeout is 72 elapsed hours and one reminder is eligible after 24 hours before expiry. Stale technical processing after 15 minutes requires Owner investigation. These are workflow timers, not a guarantee that a human responds. No separate human response SLA is invented.

Overdue means an active order whose DueAt is earlier than explicit report AsOfUtc. Active excludes Completed and Cancelled. CompletedAt equal to DueAt counts on time. Check report refresh/as-of time before discussing results. The assistant explains approved procedures; it cannot claim current order status or access inaccessible documents. Ask Owner about unsupported cases and use SharePoint for authorized current records.
