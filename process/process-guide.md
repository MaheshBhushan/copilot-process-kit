# Print order process

Owner: Owner · Version: 1.0 · Effective: 2026-10-14 · Review: 2026-11-13

This guide covers the internal pilot for one print shop, EUR prices and fewer than 50 orders each day. Sales represents the external customer. The [business contract](../contracts/process.json) defines exact choices and guards. The [BPMN model](print-order.bpmn) and [diagram](print-order.svg) show the same process. The model is descriptive BPMN 2.0.2, with complete diagram interchange; it does not execute a Power Automate flow.

## Roles and records

Sales records customer intent and consent evidence. Prepress checks artwork and prepares a quote. The Approver decides internal production approval. Production prints the released file and performs manual quality control. Owner manages exceptions. Automation processes authorized commands and records outcomes.

Orders is the read-only operational register for staff. Staff submit a new OrderCommands row for each action. They enter the current Revision as ExpectedRevision except for Submit. A stale revision rejects the command without changing the order. Staff must reread the order and decide whether a new command is still appropriate. They must never edit or delete an existing command to retry it.

RequestKey is a required unique reference of 1–100 ASCII letters, digits or hyphens, for example `sales-20261014-001`. SharePoint's immutable command ID determines OrderKey, for example command ID 123 produces `PO-000123`. The first order revision is 1. Each accepted transition increments Revision. Created By identifies the actor; a typed role, email or PayloadJson never grants permission.

## Walkthrough

1. Sales submits Title, CustomerCode, ProductType, Quantity and DueAt. Use synthetic customer code `CUST-014`, product `Flyers`, quantity `500`, title `Autumn sample flyers`, and a future UTC due date. Product choices are BusinessCards, Flyers, Posters and Booklets. Title length is 1–120; Quantity is an integer 1–100000. DueAt must follow creation. Automation records Submitted and retains the original SubmittedAt through all corrections.
2. Prepress opens the PDF in DraftArtwork and checks bleed, dimensions, fonts, color mode and resolution manually. The pilot accepts PDF only, at most 20 MB. Prepress records a checklist reference, positive QuoteEUR rounded to two decimals, same-site DraftFilePath, CustomerConsentRef and configured ApproverUPN. CustomerConsentRef identifies Sales' external consent evidence; it must not contain the full customer message. RequestChanges with a reason changes Submitted to ChangesRequested when the inputs need correction.
3. Sales corrects the business fields and submits Resubmit with a correction note in Reason. Resubmit changes ChangesRequested or ApprovalExpired to Submitted. A new approval cycle needs new validation and a new snapshot.
4. Validate changes Submitted to AwaitingApproval only after the immutable snapshot exists. Automation freezes `ProductionFiles/ApprovalSnapshots/PO-000123-r2.pdf` when entry revision is 2 and sets ApprovalKey `PO-000123-r2`. Staff cannot change that file. The approver receives that exact snapshot and the quote, quantity, deadline and consent reference.
5. The Approver approves or rejects that revision. The deadline is 72 elapsed hours from request creation. Automation sends at most one reminder after 24 hours while the deadline remains future. A matching approval response with ResponseAt at or before the deadline can change AwaitingApproval to Approved; rejection changes it to ChangesRequested and retains the reason. At or after the deadline, a matching ApprovalExpired command changes it to ApprovalExpired. The independent approval worker never blocks command dispatch.
6. Prepress releases the approved snapshot into `ProductionFiles/PO-000123-r2-approved.pdf` without overwriting an existing file. Approval acceptance increments business Revision to 3 but keeps ApprovalKey r2. The filename follows ApprovalKey. Release changes Approved to ReadyForProduction only after file identity and the successful immutable copy are verified. Approved alone does not permit printing.
7. Production uses ReleasedFilePath, assigns a configured ProductionUPN and submits StartProduction. ReadyForProduction becomes InProduction. Production checks the finished output manually. Failed QC requires physical rework and another QC check. The order stays InProduction during that loop. Complete requires QCReference and an integer WasteQuantity from 0 through Quantity. Automation records CompletedAt and Completed.

## State and exception table

| Current state | Command | Role | Next state |
|---|---|---|---|
| No order | Submit | Sales | Submitted |
| Submitted | Validate | Prepress | AwaitingApproval |
| Submitted | RequestChanges | Prepress | ChangesRequested |
| ChangesRequested | Resubmit | Sales | Submitted |
| ApprovalExpired | Resubmit | Sales | Submitted |
| AwaitingApproval | ApprovalApproved | Automation | Approved |
| AwaitingApproval | ApprovalRejected | Automation | ChangesRequested |
| AwaitingApproval | ApprovalExpired | Automation | ApprovalExpired |
| Approved | Release | Prepress | ReadyForProduction |
| ReadyForProduction | StartProduction | Production | InProduction |
| InProduction | Complete | Production | Completed |
| Submitted, ChangesRequested, ApprovalExpired, Approved, ReadyForProduction | Cancel | Sales or Owner | Cancelled |

Completed and Cancelled are terminal. Cancel always needs a reason and a matching revision. AwaitingApproval cancellation is outside this pilot's transition table. InProduction cancellation requires a separately designed exception. The diagram's interrupting cancellation subprocess has this explicit state guard. It cannot authorize a broader cancellation.

A stale approval card cannot authorize a revised order. Decisions must match ApprovalKey, requested revision and assigned response identity. A timely response processed after an expiration command is rejected because the state already changed. Owner reviews the queue and evidence; no automatic revival occurs.

Technical failure preserves business Status. Automation uses command, approval-job or notification NeedsReview state and an incident note. Owner checks LastCommandKey, revisions, deterministic event/job/message keys and file metadata before any retry. A failed notification never reverses an order decision. Staff report the OrderKey and command ID to Owner rather than submitting repeated commands.

ProductionFiles snapshots are immutable but not a records-management compliance guarantee. Administrators retain exceptional privileges. Owner must audit any administrative repair and verify approval evidence before a release. DraftArtwork edits after Validate cannot change the approved snapshot.

## Time and measurement

Store UTC ISO 8601 timestamps ending in `Z`. Site displays may use local time. Approval deadlines use elapsed hours, not working days. An active order has any status except Completed or Cancelled. It is overdue when DueAt is earlier than an explicit report AsOfUtc. Completion is on time when CompletedAt is at or before DueAt. Administrative ChangesRequested counts as administrative rework; production QC rework has a separate manual record.

## Model acceptance

Local checks parse XML, resolve node/flow references, confirm lane membership and DI shapes/waypoints, and render the SVG. Local checks do not prove BPMN XSD conformance or execution. Open the BPMN in a BPMN 2.0 modeler and inspect lane routing, labels, timer and cancellation guard before adopting it. Full XSD validation and modeler interoperability remain Pending.
