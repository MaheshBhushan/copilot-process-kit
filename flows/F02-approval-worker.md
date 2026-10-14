# F02 Approval worker

Build an automated flow with service-owned SharePoint and Standard approvals connections. Owner is recovery co-owner. Set trigger concurrency to 20. Check EnableAutomation at run start and again before Create_approval; a paused flow must not send a new card. Twenty long approval waits consume the available trigger slots; sustained New-job backlog blocks pilot expansion. F04 covers jobs that become due before a worker starts.

The flow uses separate Create and Wait actions. It never calls Start and wait from F01. [Microsoft's Standard approvals reference](https://learn.microsoft.com/en-us/connectors/approvals/) lists separate creation/wait operations and dynamic outputs. Bind outputs through the actual designer and capture the observed shape. Use the shared [ETag recipe](expressions.md), including entity type and conditional 412 handling.

## Designer actions

| # | Stable action name | Native connector / visible action | Inputs and expressions | Run after / retry | Output and verification |
|---|---|---|---|---|---|
| 1 | `Job_created` | SharePoint / When an item is created | ApprovalJobsListId; trigger concurrency On=20; do not use modified trigger. | Trigger / N | Approval wait occupies only this worker. |
| 2 | `Config` | Data Operations / Compose | Load same config as F01; require EnableAutomation=true. | S / N | False terminates success before claim. |
| 3 | `Read_job_ETag` | SharePoint / Send an HTTP request to SharePoint | Fresh verbose GET job ID and configured entity type. | Enabled / R | Capture actual ETag; no wildcard. |
| 4 | `Job` | Data Operations / Compose | body('Read_job_ETag')?['d']; normalize choices if needed. | S / N | Trusted fresh job fields. |
| 5 | `Job_ETag` | Data Operations / Compose | body('Read_job_ETag')?['d']?['__metadata']?['etag'] | S / N | Missing metadata => review, no approval. |
| 6 | `Job_author_email` | Data Operations / Compose | Bind immutable job Created By email from fresh GET expanded Author or SharePoint Get item, not trigger payload. If REST AuthorId only, add Get item to resolve Author Email. | S / R | toLower(trim(...)) must equal AutomationUPN. |
| 7 | `Get_order` | SharePoint / Get items | Validated OrderKey exact filter; Top Count=2; require one. | S / R | Current order, never accept missing/duplicates. |
| 8 | `Order` | Data Operations / Compose | first(body('Get_order')?['value']) after exactly-one guard. | S / N | Normalize choice strings. |
| 9 | `Guard_job` | Control / Condition | New; service Author; nonempty ETag; one configured AssignedUPN with Approver role; current AwaitingApproval/key/revision/snapshot/quote/deadline match; deadline future. | S / N | Already obsolete jobs get NeedsReview; no creation. A due job enqueues expiry without creating. |
| 10 | `Claim_job` | SharePoint / Send an HTTP request to SharePoint | Conditional MERGE using Job_ETag; JobState=Creating, StartedAt=UTC. Example in expressions.md. | Guard true / N | 204 owns claim; 412 exits success without create; uncertain => review only. |
| 11 | `Create_approval` | Standard approvals / Create an approval | Approval type Approve/Reject – First to respond; exactly AssignedUPN; title OrderKey / RequestedRevision; details below; item link immutable snapshot; enable reassignment=false. | Claim 204 / N | Capture real Approval ID; creation may send connector notifications. |
| 12 | `Approval_id` | Data Operations / Compose | Designer Approval ID dynamic output of Create_approval; gate on nonempty. | S / N | Observed dynamic path recorded in evidence. |
| 13 | `Persist_approval` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag conditional MERGE ApprovalId=Approval_id, JobState=Waiting. | S / N | Persist immediately before waiting; uncertain write rereads ID/state; no second Create. |
| 14 | `Wait_approval` | Standard approvals / Wait for an approval | Approval ID=Approval_id; action timeout PT72H; retry None. | Persistence confirmed / N | Only independent worker waits; authoritative deadline remains persisted UTC. |
| 15 | `Response_outcome` | Data Operations / Compose | Bind actual Outcome; require exactly Approve or Reject. | Wait succeeded / N | Missing/unknown goes to NeedsReview. |
| 16 | `Response_upn` | Data Operations / Compose | Bind single responder UPN; normalize lowercase/trim; require equality AssignedUPN. | S / N | Do not use displayed name/email alias as identity without verified UPN mapping. |
| 17 | `Response_at` | Data Operations / Compose | Bind actual single response date/time; valid UTC Z; never utcNow() as response time. | S / N | Capture output and normalized UTC evidence. |
| 18 | `Response_reason` | Data Operations / Compose | Actual approval comments for Reject; trimmed fallback Internal approver rejected without comments only when outcome is verified Reject. | S / N | Comments plain text; never rendered as unescaped HTML. |
| 19 | `Persist_response` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE Outcome, ResponseUPN, ResponseAt. Retain Waiting until command ensured. | Validated response / N | Durable response precedes enqueue; F01 may read it while job is Waiting. |
| 20 | `Get_current_order` | SharePoint / Get items | Reread exact order and current key/revision. Compare response time to deadline, not processing clock. | S / R | Already expired/revised => record review, no revival. |
| 21 | `Ensure_decision_command` | SharePoint / Create item | GET by unique RequestKey first; if absent create exact payload below; compare existing immutable fields on conflict. | Still matching and timely / N | Uses Automation connection so immutable Author is service. |
| 22 | `Mark_decision_queued` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE JobState=DecisionQueued, FinishedAt=UTC; preserve response fields. | Command exists and agrees / N | F01 may already have applied decision; do not revert order. |
| 23 | `Ensure_expiry_command` | SharePoint / Create item | GET unique ApprovalKey-expired then create/compare payload. Run only when authoritative deadline reached; timeout before deadline routes NeedsReview. | Wait timed out or due-before-create / N | No assumed approval-card cancellation. |
| 24 | `Mark_expired` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE JobState=Expired, FinishedAt=UTC only after matching expiry command ensured and no persisted timely response. | Expiry branch / N | Job Expired does not mutate business Status; F01 decides transition. |
| 25 | `Review_job` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE JobState=NeedsReview, ErrorDetail; retain ApprovalId/response if known. Catch failed/timed out Create, persistence, wait or uncertain enqueue. | F/T / N | Owner reconciles approval center by OrderKey/key/title/run before retry. |

## Card and command fields

Card Title=`OrderKey / rRequestedRevision`; Details contains Quantity, SnapshotQuoteEUR, DueAt, CustomerConsentRef and the absolute same-site immutable snapshot link. Use Orders values only after equality with the job/receipt is proven. No attachment, external approver or reassignment is enabled. Approvals connector notifications are a separate side effect from F03. During dispatcher-only verification keep F02 disabled or set Create_approval Enable notifications=false if the actual selected approval action exposes that option; otherwise use only authorized internal test recipients. Record which setting exists. EnableNotifications=false only suppresses F03 and cannot promise silence from approvals.

Decision command fields: Title=RequestKey; RequestKey=ApprovalKey-approved for verified Approve, ApprovalKey-rejected for verified Reject; OrderKey=Job.OrderKey; CommandType=ApprovalApproved/ApprovalRejected; ExpectedRevision=Job.RequestedRevision; ApprovalKey=Job.ApprovalKey; ResponseUPN=normalized actual responder; ResponseAt=actual response timestamp; Reason=verified reject comments/fallback; ProcessingState=Pending. All other business fields unset. Never accept arbitrary cards/outcomes or caller-created response data as approval evidence.

Expiry command: Title/RequestKey=ApprovalKey-expired; OrderKey; CommandType=ApprovalExpired; ExpectedRevision=RequestedRevision; ApprovalKey; ProcessingState=Pending; response fields unset. F04 uses identical immutable payload. Unique-key collision requires a GET and payload comparison. A different Author or payload means NeedsReview. If wait returns late, persist observed response for audit and route review; do not create a usable timely command.

## Time and queue ordering

F01 accepts a verified response when ResponseAt <= DeadlineUtc and the current order remains AwaitingApproval with matching ApprovalKey and RequestedRevision, even when processing happens later. F02 must use the same predicate after Wait. A decision already persisted or queued when expiry competes requires Owner review; F01 never revives ApprovalExpired. Owner reads actual card response time, command IDs and run times, records the decision, and uses a supported new cycle or an explicitly approved administrative incident procedure. Owner does not backdate a response or silently rewrite state. An already expired order rejects an old card after Resubmit as well.

PT72H bounds the Wait action; persisted deadline starts at Validate, so a delayed worker can wait past the deadline. F04 enqueues authoritative expiry while the wait remains active. A 72-hour wait remains inside the documented [30-day cloud-run limit](https://learn.microsoft.com/en-us/power-automate/limits-and-config). Timeout does not prove that an approval card was cancelled. Owner checks the approval center and cancels obsolete cards where supported.

## Uncertainty and cleanup

Never retry Create_approval automatically. Failure or timeout can mean a card exists. A successful Create followed by a failed Persist requires manual approval-center reconciliation; do not reset JobState=New or rerun the whole flow. Owner matches key/revision/title/assigned user, records the real ID, and resumes a wait on that existing ID only through a reviewed recovery run. If no unique card can be proved, retain NeedsReview and prevent production. If a claim succeeded but its response was lost, the worker does not assume ownership. Duplicate-trigger 412 is handled as a successful no-op. F04 flags stale Creating after 15 minutes; it does not create another card. Finished jobs and obsolete cards remain in audit retention; no automatic deletion is required.
