# Order lifecycle

Authority: process contract 1.0. Owner approves changes before republication. This guide explains procedures; it contains no live order data.

Sales submits Title, CustomerCode, ProductType, Quantity and DueAt through OrderCommands. Quantity is an integer from 1 to 100000; ProductType is BusinessCards, Flyers, Posters or Booklets. DueAt must be future UTC. Orders begins at Submitted, Revision 1. SubmittedAt retains the initial timestamp through corrections.

Prepress uses Validate to move Submitted to AwaitingApproval after a positive QuoteEUR, existing PDF DraftFilePath, CustomerConsentRef, allowlisted ApproverUPN and PreflightChecklistRef pass checks. Prepress can use RequestChanges with Reason to move Submitted to ChangesRequested. Sales uses Resubmit from ChangesRequested or ApprovalExpired with valid updated business fields and a correction Reason to return to Submitted.

Automation applies ApprovalApproved to reach Approved or ApprovalRejected with decision Reason to reach ChangesRequested. Automation applies ApprovalExpired to reach ApprovalExpired. The approval guards in Approval and exceptions apply to every decision.

Prepress uses Release from Approved to ReadyForProduction after copying the approved immutable snapshot successfully. Production uses StartProduction with configured ProductionUPN from ReadyForProduction to InProduction. Production uses Complete after successful manual QC with QCReference and integer WasteQuantity between zero and Quantity. The dispatcher records completion time and changes status to Completed. Failed QC loops through manual rework and QC without a new business state.

Sales or Owner can Cancel with Reason from Submitted, ChangesRequested, ApprovalExpired, Approved or ReadyForProduction. AwaitingApproval and InProduction cancellation are excluded. Escalate those requests to Owner without changing status. Completed and Cancelled are terminal. Rejected is a command outcome, never an order status.

Every accepted transition increments Revision. Commands except Submit require ExpectedRevision. Read the latest order before submitting; StaleRevision means no mutation. Do not resubmit a duplicate blindly. Staff cannot edit authoritative Orders directly. Technical failure leaves business Status intact and requires Owner review of command/job/outbox NeedsReview.
