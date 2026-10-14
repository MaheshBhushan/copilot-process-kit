# F03 Notification worker

Build a scheduled flow with dedicated SharePoint, Office 365 Outlook and Microsoft Teams service connections, Owner co-owner, 2-minute UTC recurrence and concurrency 1. Poll only when both feature flags are true. Use one outbox row per channel, so successful email and uncertain Teams delivery can be reconciled independently. No notification changes Orders.Status.

## Designer actions

| # | Stable action name | Native connector / visible action | Inputs and expressions | Run after / retry | Output and verification |
|---|---|---|---|---|---|
| 1 | `Poll_outbox` | Schedule / Recurrence | Every 2 minutes, UTC; trigger concurrency On=1. | Trigger / N | Record settings. |
| 2 | `Config` | Data Operations / Compose | Shared config; require EnableAutomation AND EnableNotifications. | S / N | False finishes without touching Pending backlog. |
| 3 | `Get_outbox` | SharePoint / Get items | OutboxListId; DeliveryState eq 'Pending'; Order By ID asc; Top Count=25; pagination Off. | Enabled / R | Sequential oldest-first batch. |
| 4 | `For_each_message` | Control / Apply to each | body('Get_outbox')?['value']; concurrency Off. | S / N | Try_message/Catch_message scopes per item. |
| 5 | `Get_message` | SharePoint / Get item | Fresh row by loop ID; immutable Author must be AutomationUPN. | Loop / R | Human-created/altered message fails review. |
| 6 | `Message` | Data Operations / Compose | Normalize Choice fields; parse only trusted service SafePayload via Parse JSON with OrderKey/Status/OrderLink properties. | S / N | No supplied HTML or arbitrary destination. |
| 7 | `Guard_message` | Control / Condition | Still Pending; known template/channel; recipient exact internal configured Sales/Owner identity, configured assigned Approver for reminder only, or ChannelId; trusted payload/OrderLink same site; current EnableNotifications before sending. | S / N | False leaves paused row Pending, invalid data NeedsReview. |
| 8 | `Read_outbox_ETag` | SharePoint / Send an HTTP request to SharePoint | Fresh GET with verbose mode, state must still Pending; actual entity type. | Guard true / R | Fresh ETag for conditional claim. |
| 9 | `Claim_message` | SharePoint / Send an HTTP request to SharePoint | Conditional MERGE DeliveryState=Sending, AttemptCount=old+1, LastAttemptAt=UTC. | S / N | 412 skips send; uncertain claim becomes review. |
| 10 | `Choose_channel` | Control / Switch | Email or Teams; Default NeedsReview. | Claim 204 / N | One row invokes exactly one send/post. |
| 11 | `Send_email` | Office 365 Outlook / Send an email (V2) | Email case: To=validated Recipient; Subject=[OrderKey] TemplateKey; safe body below; no attachments; retry None in Settings. | Email case / N | Success acknowledges send; absence of provider ID does not imply failure. |
| 12 | `Post_teams` | Microsoft Teams / Post message in a chat or channel | Teams case: Post as=Flow bot if tenant allows; Post in=Channel; Team=TeamId; Channel=ChannelId; safe body; retry None. | Teams case / N | Capture actual message ID if returned; no customer/artwork attachments. |
| 13 | `Mark_sent` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE DeliveryState=Sent, DeliveredAt=UTC; ProviderReference only actual returned ID (nullable). | Chosen send/post succeeded / N | Do not rerun send if status persistence fails. |
| 14 | `Review_delivery` | SharePoint / Send an HTTP request to SharePoint | Fresh ETag MERGE NeedsReview/ErrorDetail on failed/timed out send/post or failed sent persistence; retain attempt evidence. | F/T / N | Watchdog catches stale Sending if review write fails. |

## Fixed safe templates

TemplateKey allowlist is `submitted`, `changes-requested`, `approved`, `ready`, `completed`, `cancelled`, `approval-expired`, `reminder`, `incident`. Render fixed prose from TemplateKey; interpolate validated OrderKey, captured Status and trusted Orders link only. `approved` says internal approval recorded; `ready` says released file is available through ProductionQueue. Never tell Production to print from Approved alone. Reminder names the order and remaining deadline through the order page; incident directs Owner to NeedsReview. Render links from trusted SiteUrl/list ID/item ID, escape plain text for Outlook HTML, and use no arbitrary HTML from SafePayload.

SafePayload captures the status at event time. Deliver backlog as historical event notification, not a claim of current state; body says `Recorded status: <Status>. Open the order for current status.` Recipient is resolved from trusted order SalesUPN or configured OwnerUPN; incidents/expiry go to Owner. Teams uses only configured internal pilot channel. Record actual accepted Team/Channel settings and identities in evidence.

## One automatic attempt and manual reconciliation

Send_email and Post_teams have retry policy None. Claim_message precedes them. A timeout can follow successful delivery. Review_delivery must not reset Pending or decrement AttemptCount. Failure after Mark_sent also leaves uncertain evidence; do not send again. F04 marks old Sending as NeedsReview after 15 minutes.

Owner inspects automation Sent Items and the configured Teams channel using MessageKey/run time/order/template, preserves actual message IDs/links, and determines delivered/not-delivered/uncertain. If delivered, mark Sent with observed delivery evidence. If conclusively not delivered, record the inspection and approved retry reason, then reset only that row Pending. If uncertain, keep NeedsReview and contact the intended internal recipient through a separately authorized process. A new automatic run never chooses to retry uncertain delivery. This policy bounds duplicate automatic attempts; it cannot prove exactly-once delivery or receipt by a human. Owner can see list NeedsReview views even if incident messaging also fails. Keep messages and audit rows according to the recorded retention policy.
