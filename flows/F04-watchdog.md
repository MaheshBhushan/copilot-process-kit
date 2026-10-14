# F04 Watchdog

Build a scheduled service-owned flow with Owner co-owner, 15-minute UTC recurrence and trigger concurrency 1. It does not write Orders or execute cards/sends. It creates deterministic commands/outbox entries and flags uncertain work. EnableNotifications controls only delivery; reminders/incidents can queue while F03 is paused. All four flows follow [shared paging and retry limits](README.md).

Each candidate uses a fresh read, exact state and timestamp predicate, and conditional ETag update. F04 must not overwrite a command just marked Applied, a job just marked Waiting/DecisionQueued, or a message just marked Sent. Use separate list loops; a temporary object array is optional, not a new service or child flow.

## Designer actions

| # | Stable action name | Native connector / visible action | Inputs and expressions | Run after / retry | Output and verification |
|---|---|---|---|---|---|
| 1 | `Watch_schedule` | Schedule / Recurrence | Every 15 minutes; UTC; concurrency On=1. | Trigger / N | No external wait. |
| 2 | `Config` | Data Operations / Compose | Shared config; require EnableAutomation=true. | S / N | False no writes. |
| 3 | `Watch_time` | Data Operations / Compose | formatDateTime(utcNow(),'yyyy-MM-ddTHH:mm:ssZ'); one captured instant for run predicates. | Enabled / N | Record UTC cutoff. |
| 4 | `Get_waiting` | SharePoint / Get items | JobState eq 'Waiting'; indexed filter; pagination On=1000; order ID asc. | S / R | Deadline predicates evaluated inside loop; count=1000 warns Owner ceiling reached. |
| 5 | `For_each_waiting` | Control / Apply to each | Waiting rows sequential; fresh Get item in each body; normalize as Job. | S / N | Recheck Waiting and service Author. |
| 6 | `Get_current_order` | SharePoint / Get items | Exact validated OrderKey; Top Count 2; require one. | Loop / R | Match AwaitingApproval/key/revision before reminder/expiry. |
| 7 | `Choose_deadline_path` | Control / Condition | Watch_time >= DeadlineUtc => expiry; else if Watch_time >= DeadlineUtc-48h => reminder; else no-op. Validate nonempty UTC dates first. | S / N | Deadline-48h equals request+24h under mandatory 72h configuration. |
| 8 | `Ensure_watch_expiry` | SharePoint / Create item | Due path: GET RequestKey=ApprovalKey-expired first; create identical F02 expiry payload only if absent; full compare on conflict. Do not enqueue if known timely response or decision already queued; flag race for review. | Due matching current order / N | F01 alone changes status; independent watchdog survives dead worker. |
| 9 | `Ensure_reminders` | Control / Apply to each | Future deadline path: Email and Teams sequential; GET MessageKey first then Create item if missing; compare on conflict. Payload below. | 24h reached and future / N | At most one reminder per key/channel; no reset after delivery. |
| 10 | `Get_unstarted_jobs` | SharePoint / Get items | JobState eq 'New'; indexed; pagination=1000; fresh per-row reads; due jobs enqueue same expiry without card. Old unstarted jobs produce incident, not another job. | After Waiting loop / R | Covers approval trigger backlog at 20-run limit. |
| 11 | `Get_processing` | SharePoint / Get items | ProcessingState eq 'Processing'; pagination=1000; keep ProcessingStartedAt <= Watch_time-15m in loop. | S / R | Missing timestamp is an incident, never permission to reset. |
| 12 | `Get_creating` | SharePoint / Get items | JobState eq 'Creating'; pagination=1000; keep StartedAt <= Watch_time-15m in loop. | S / R | Do not create another approval. |
| 13 | `Get_sending` | SharePoint / Get items | DeliveryState eq 'Sending'; pagination=1000; keep LastAttemptAt <= Watch_time-15m in loop. | S / R | Do not resend. |
| 14 | `For_each_stale` | Control / Apply to each | Three separate sequential loops For_each_stale_command / For_each_stale_job / For_each_stale_message; fresh REST GET/ETag for every candidate. | Each query S / R | Capture actual state/timestamp before conditional write. |
| 15 | `Mark_stale_review` | SharePoint / Send an HTTP request to SharePoint | Expand one action per stale list; fresh ETag conditional MERGE appropriate state=NeedsReview and safe ErrorDetail; recheck old state/cutoff. | Stale guard true / N | 412 reread then no-op if no longer stale; never override newer progress. |
| 16 | `Ensure_incident` | SharePoint / Create item | GET unique incident key; absent create Owner Email incident; matching existing counts as reconciled. Include safe order key/status/link only. | Stale/race/ceiling detected / N | No recursive incident for uncertain incident delivery; Owner checks views. |
| 17 | `Watch_failure` | Control / Scope | Catch failed/timed out reads/writes; keep business status; record redacted run error and notify Owner via available deterministic incident if safe. | F/T / N | If SharePoint unavailable, Owner inspects failed flow run and list views on recovery. |

## Exact watchdog payloads

Expiry payload is identical to [F02](F02-approval-worker.md): deterministic RequestKey=ApprovalKey-expired, OrderKey, CommandType=ApprovalExpired, ExpectedRevision=RequestedRevision, ApprovalKey, ProcessingState=Pending, Title=RequestKey. Validate the current order before enqueue. A known timely persisted response or queued decision creates an Owner queue-race incident; never automatically force expiration over that evidence. F01 repeats guards at application time. F04 does not set job Expired merely because it queued a command. A worker may still return a card response, and evidence must remain available.

Reminders: MessageKey=ApprovalKey-reminder-Email and ApprovalKey-reminder-Teams; Title=MessageKey; OrderKey; TemplateKey=reminder; Channel; Email Recipient=AssignedUPN (configured Approver), Teams Recipient=ChannelId; SafePayload contains only order key, recorded AwaitingApproval status and Orders link; DeliveryState=Pending; AttemptCount=0. F03 recipient allowlist must include the exact assigned configured Approver for reminders, in addition to Sales/Owner for routine messages. No reminder once deadline <= Watch_time or key/revision/state changed. DeadlineUtc minus 48 elapsed hours is exactly request+24h with the required 72h deadline; assert config 72/24. A changed SLA requires updating this predicate to DeadlineUtc-ApprovalTimeoutHours+ReminderHours and retesting.

Incidents use MessageKey=`incident-<Commands|ApprovalJobs|Outbox>-<ID>-Email` for stale rows, `incident-<ApprovalKey>-queue-race-Email` for ordering conflicts, or `incident-watch-<UTC-date>-<query-name>-Email` for a query ceiling. Channel=Email; Recipient=OwnerUPN; TemplateKey=incident; safe order link only. For a stale Submit with no persisted OrderKey, derive PO-padded command ID. Malformed rows without a safe key stay visible in the source NeedsReview view and failed-run evidence; do not invent an order. A source Outbox incident becoming uncertain does not generate further incidents recursively.

Missing dates, mismatching immutable payload, invalid Author, conflicting key or missing current order are Owner incidents. Never reset Processing→Pending, Creating→New or Sending→Pending automatically. Owner follows [recovery](../deployment/runbook.md). Query failures/throttling use bounded read retries and retain backlog. No spin loops, automatic whole-run resubmission, or assumed exactly-once effects exist.
