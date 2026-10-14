# Expression and binding cookbook

Expressions below use Power Automate workflow syntax. Paste them into Expression without a leading `@`. Inline JSON expression values use `@{...}`. Run [binding probes](../deployment/runbook.md) before enabling. Missing identity, choice, ETag, response time or deadline fails closed. Do not coalesce those into permission or success.

## Stable bindings

F01 Compose `Command` = body of `Get_command`; `ActorUPN` = immutable Created By Email dynamic content from `Get_command`, normalized below. `CommandKey`, `OrderKey`, `OldRevision`, `NewRevision`, `TransitionAt`, `ApprovalKey`, `DeadlineUtc`, `Plan` are variables initialized outside the sequential loop and reset per command. `Config` is a Compose object matching [environment keys](../config/environment.example.json). `Order` is Compose of the single returned order object after count=1. F02 uses `Job` Compose from fresh REST GET body. F03 uses `Message` Compose from fresh Get item. F04 uses sequential named loops per query.

Connector shapes are an enablement gate. Capture redacted outputs and use designer dynamic content to bind Created By Email, Editor Email, file UniqueId/Identifier/version/size, Approval ID, outcome, response UPN, response date and comments. Rename normalization Compose actions exactly as specified. Never invent a JSON path for dynamic approval outputs. Standard Approvals publishes dynamic output schemas; a local document cannot prove a tenant binding. Map native Choice Value to strings in `Command`, `Order`, `Job` and `Message` if connector output is an object. Preserve all other fields.

```text
# Command IDs and author
concat('CMD-',string(outputs('Command')?['ID']))
toLower(trim(outputs('Author_email')))
concat('PO-',formatNumber(int(outputs('Command')?['ID']),'000000'))
# Role lookup: ActorUPN must be nonempty; absent mapping returns [], never a role
coalesce(outputs('Config')?['AllowedRoles']?[outputs('ActorUPN')],json('[]'))
contains(outputs('Actor_roles'),'Prepress')
and(equals(outputs('ActorUPN'),toLower(trim(outputs('Config')?['AutomationUPN']))),contains(outputs('Actor_roles'),'Automation'))
# Order lookup, ONLY after identifier grammar passes
concat('OrderKey eq ''',variables('OrderKey'),'''')
length(body('Get_order')?['value'])
first(body('Get_order')?['value'])
int(outputs('Order')?['Revision'])
add(variables('OldRevision'),1)
equals(outputs('Order')?['LastCommandKey'],variables('CommandKey'))
concat(variables('OrderKey'),'-r',string(variables('NewRevision')))
formatDateTime(utcNow(),'yyyy-MM-ddTHH:mm:ssZ')
addHours(variables('TransitionAt'),int(outputs('Config')?['ApprovalTimeoutHours']))
# Response checks: date presence and valid UTC syntax checked in an earlier Condition
lessOrEquals(ticks(outputs('Command')?['ResponseAt']),ticks(outputs('Job')?['DeadlineUtc']))
greaterOrEquals(ticks(variables('TransitionAt')),ticks(outputs('Job')?['DeadlineUtc']))
# F02 matches current AwaitingApproval, NOT current clock before deadline for response acceptance
and(equals(outputs('Order')?['Status'],'AwaitingApproval'),equals(outputs('Order')?['ApprovalKey'],outputs('Job')?['ApprovalKey']),equals(int(outputs('Order')?['Revision']),int(outputs('Job')?['RequestedRevision'])))
# Reminder: strict future deadline, 24 elapsed hours
and(greaterOrEquals(ticks(utcNow()),ticks(addHours(items('For_each_waiting')?['DeadlineUtc'],sub(int(outputs('Config')?['ReminderHours']),int(outputs('Config')?['ApprovalTimeoutHours']))))),less(ticks(utcNow()),ticks(items('For_each_waiting')?['DeadlineUtc'])))
# Stable keys
concat(outputs('Job')?['ApprovalKey'],'-approved')
concat(outputs('Job')?['ApprovalKey'],'-rejected')
concat(outputs('Job')?['ApprovalKey'],'-expired')
concat(outputs('Job')?['ApprovalKey'],'-reminder-Email')
concat(outputs('Job')?['ApprovalKey'],'-reminder-Teams')
concat(variables('OrderKey'),'-r',string(variables('NewRevision')),'-',variables('Channel'))
concat(outputs('Config')?['LibraryPaths']?['ApprovalSnapshots'],'/',variables('ApprovalKey'),'.pdf')
concat(outputs('Config')?['LibraryPaths']?['ProductionFiles'],'/',outputs('Order')?['ApprovalKey'],'-approved.pdf')
# Path boundary, plus separate decoded-segment checks described below
and(startsWith(variables('DraftPath'),concat(outputs('Config')?['LibraryPaths']?['DraftArtwork'],'/')),endsWith(toLower(variables('DraftPath')),'.pdf'),not(contains(variables('DraftPath'),'..')),not(contains(variables('DraftPath'),'://')))
# Outbox attempt and stale cutoff
add(int(coalesce(outputs('Message')?['AttemptCount'],0)),1)
addMinutes(utcNow(),-15)
```

## Native validation actions

Use Condition before conversions. Native expressions have no general regex matcher. Validate OrderKey by split `-`, exactly two segments, first `PO`, second length >=6, and remove digits with nested `replace` calls; the remainder must be empty. For ApprovalKey require three segments, valid OrderKey first two, third prefix `r`, positive integer suffix with no leading zero and only digits. Require `RequestKey` length 1–100. Apply to each `range(0,length(...))` sequentially; `substring(...,item(),1)` must occur in `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-`. Set Boolean `IdentifierValid` false on any failure. The table's `Validate_identifiers` scope contains these native Condition/Apply to each/Set variable actions; record their generated names in tenant evidence. No external regex service is needed.

Validate Quantity with `isInt(string(...))` then range 1–100000. Validate ExpectedRevision and WasteQuantity similarly before `int`; use contract bounds. Validate QuoteEUR with `isFloat(string(...))`, positive and `equals(float(...),float(formatNumber(float(...),'0.00','en-US')))`. ProductType must occur in the contract's four-item array. Title must be trimmed nonempty and <=120 characters; CustomerCode must be trimmed nonempty, synthetic, and contain no `@`. Required reasons/references must be trimmed nonempty. Reject string dates without trailing `Z`; parse in a Try scope using `ticks`, catch malformed values to Rejected/InvalidInput. Never evaluate `ticks` on null. Submit DueAt > immutable command Created; Resubmit DueAt > TransitionAt. UTC elapsed hours do not use Berlin wall time.

Accept only decoded server-relative paths under exact DraftArtwork + `/` on SiteUrl. Reject `://`, `..`, query/fragment, backslash and encoded traversal/separators (`%`, including double encoding) for this pilot; reject empty segments after the root. Do not concatenate unvalidated paths into REST. Get file metadata using path must succeed and size <=20971520 bytes. Native metadata does not certify fonts, bleed, resolution, color, consent or print dimensions; Prepress signs the referenced checklist manually.

## ETag conditional updates

Use SharePoint **Send an HTTP request to SharePoint** with Site Address=SiteUrl. GUIDs come only from config; item ID is an integer from a trusted list read. Generic HTTP is unnecessary.

```http
GET _api/web/lists(guid'<ApprovalJobsListId>')/items(<ID>)
Accept: application/json;odata=verbose
```

With verbose JSON, bind `Job` to `body('Read_job_ETag')?['d']` and Compose `Job_ETag` to `body('Read_job_ETag')?['d']?['__metadata']?['etag']`. Record actual shape in evidence; if the connector negotiates a different mode, update both mapping and Accept consistently before enabling. Missing ETag is NeedsReview, never `*`.

```http
POST _api/web/lists(guid'<ApprovalJobsListId>')/items(<ID>)
Accept: application/json;odata=verbose
Content-Type: application/json;odata=verbose
IF-MATCH: <Job_ETag including quotes>
X-HTTP-Method: MERGE

{"__metadata":{"type":"<actual ListItemEntityTypeFullName>"},"JobState":"Creating","StartedAt":"<UTC>"}
```

Obtain ListItemEntityTypeFullName with GET `_api/web/lists(guid'<ApprovalJobsListId>')?$select=ListItemEntityTypeFullName`; bind `d.ListItemEntityTypeFullName`, never derive a name from a display title. Use the same pattern for conditional command, order and outbox updates with their actual entity types and fresh ETags. Add only schema fields. A 204 acknowledges the update. A 412 means the read is stale; reread and compare state. F02 duplicate claim exits successfully without Create; other conflicts become NeedsReview if a partial transition exists. All MERGEs use N; resolve uncertain responses by read, not replay. [Microsoft REST documentation](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/complete-basic-operations-using-sharepoint-rest-endpoints) describes MERGE and ETag concurrency.

## Receipt and effect comparison

`PayloadJson` from a staff-created command is untrusted. F01 ignores it during authentication and validation. After all guards and before business mutation, F01 replaces it with its own JSON receipt. Receipt contains CommandID, RequestKey, ActorUPN, Role, FromStatus, ToStatus, OldRevision, NewRevision, TransitionAt, Plan, ApprovalKey, and file source/snapshot/released UniqueId, version/ETag, size and paths when applicable. Persist known file identity immediately after each copy and before Orders update. Do not treat a caller's JSON as evidence. Recovery requires list version history proving the automation identity wrote the receipt after ProcessingStartedAt; check Editor and earlier version diffs under Owner review. Receipt absence, tampering, missing version evidence or mismatching payload means NeedsReview.

Existing event must match every business field (including CommandID, actor, revision, timestamp and statuses); existing job must match key/order/requested revision/assigned UPN/deadline/snapshot path/quote; outbox must match key/order/channel/recipient/template/safe payload. Mutable job/delivery progress may advance; compare immutable fields and inspect progress separately. Never overwrite an existing conflicting key.
