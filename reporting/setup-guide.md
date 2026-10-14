# Build and verify the report

The kit supplies source code and a report specification. Power BI Desktop execution, PBIX creation, tenant refresh, sharing and live usage analytics are **Pending**. Local checks reconcile CSV facts with expected values. They cannot execute M or DAX.

## Build from local CSV

1. Run [the generator](../scripts/generate_samples.py). Install/open authorized Power BI Desktop separately. Create a blank report. All sample identities and customer codes are synthetic.
2. Create a Text parameter `DataFolder` containing the absolute path to `data` without a final slash. Paste [prepare.pq](prepare.pq) into a blank query named `fxPrepare`. Paste [local-sources.pq](local-sources.pq) into `LocalSources`.
3. Create four blank queries named `Orders`, `Events`, `Usage`, `Users` with expressions `= LocalSources[Orders]`, `= LocalSources[Events]`, `= LocalSources[Usage]`, `= LocalSources[Users]`. Disable load for the function/source record. Enable load for the four tables. Review errors before loading. CSV imports use UTF-8, quoted fields and explicit types. Blank cells become null. Timestamps parse as UTC datetimezone and convert to UTC datetime for the model. The model does not retain a timezone type.
4. Paste [approval-facts.pq](approval-facts.pq) into `ApprovalFacts`. This table joins each successful decision to exactly one Validate event using ApprovalKey **and** OrderKey. It calculates elapsed hours from event timestamps. It rejects missing/duplicate requests and durations outside 0–72 hours. It does not use the current Orders approval timestamps or trust the supplied event duration.
5. Apply queries. Create the two calculated tables and each measure separately from [measures.dax](measures.dax). Mark `Date` as the date table with `Date[Date]`. Set WeekStart/SubmittedDate/CompletedDate/EventDate to Date, AsOfUtc to Date/Time, integer fields to Whole number, EUR to Fixed decimal number, hours to Decimal number and eligible cohort to True/False. Display currency as EUR and percentages with two decimals. Set WeekLabel to sort by WeekStart. Disable automatic date/time tables for clarity.
6. Create the relationships below and inspect their cardinality and direction. Build [the layout](dashboard-layout.md). Clear all slicers and compare [expected metrics](../data/expected-metrics.json). Use weekly Monday axis values for the adoption chart. Round ratios and hours to six decimals only for reconciliation; do not round source durations.
7. Exercise blank denominators and empty date ranges. Verify BLANK for rate measures when denominators are zero. Verify the late-completion scenario, rejection/new approval-key pair and expired approval example. Save a PBIX only after Desktop opens, refreshes and reconciles the report. Record actual Desktop version, refresh time, screenshots, results and report file path in [the evidence template](../deployment/evidence-template.md). These steps remain Pending.

| From (one) | To (many) | Activity | Filter direction |
|---|---|---|---|
| Orders[OrderKey] | Events[OrderKey] | Active | Single |
| Orders[OrderKey] | ApprovalFacts[OrderKey] | Active | Single |
| Date[Date] | Orders[SubmittedDate] | Active | Single |
| Date[Date] | Orders[CompletedDate] | Inactive | Single |
| Date[Date] | Usage[EventDate] | Active | Single |
| Users[UserKey] | Usage[UserKey] | Active | Single |

Leave `AsOf` disconnected with exactly one selected UTC cutoff. Leave Events EventDate without an active Date relationship to avoid a second path through Orders. Operational events and approval measures follow the selected **submission cohort**. The completion trend uses `USERELATIONSHIP` and disables the submission relationship using `CROSSFILTER`. Do not join Usage to Orders. Do not connect Users to Orders through a second path. User/role adoption slicers use Users; operational order roles are outside that adoption slicer.

The Date expression spans submission, completion, due, event and usage dates. WeekStart means Monday in UTC. Weekly Agent Users counts distinct session users inside the current date filter; show WeekStart on the chart axis. AgentSessions includes successful, failed and escalated attempts. Training counts successful TrainingCompleted records for eligible users in the selected period. Its denominator counts eligible Users in the selected role/user cohort and ignores Date. With no user/role filters, the sample denominator is 12. Label filtered training results as “completion during selected period.”

## Connect operational lists later

1. Complete [deployment gates](../deployment/runbook.md) and obtain approved read access. Inspect `SharePoint.Tables(SiteUrl, [Implementation="2.0", ViewMode="All"])` in Navigator. Record the **actual** Id values and Items column names. List GUIDs and custom internal names must match the verified source. MissingField.Error deliberately stops a mismatched projection. Add an explicit rename step only after observing returned names. Do not guess display names.
2. Create Text parameters SiteUrl, OrdersListId, EventsListId and Logical parameter SharePointNaiveIsUtc=false. Paste [sharepoint-sources.pq](sharepoint-sources.pq) as `SharePointSources`. Replace only the Orders and Events query expressions with `= SharePointSources[Orders]` and `= SharePointSources[Events]`. Keep the same preparation and approval-facts queries. Authenticate with the approved organizational account. The connector projects primitive/text key fields and avoids unnecessary lookup expansion.
3. Inspect returned timestamp types against known UTC order/event records. Zoned values normalize to UTC. Unzoned datetime values fail unless SharePointNaiveIsUtc=true. Enable this setting only after proving that the connector's returned naive values represent UTC. If the connector returns local wall time, convert using a verified offset/timezone procedure before `fxPrepare`; do not merely label local time UTC. Record DST checks and site locale. Keep nullable timestamps null.
4. Reconcile operational records with real list/event IDs and the report reconciliation tenant case. Set the disconnected AsOf row to an explicit reviewed UTC cutoff and display it on the report. Record extraction/refresh timestamp separately. Refresh credentials, list visibility, dataset permissions, capacity/user licenses and sharing require tenant verification. List 2.0 lookup limits apply. See [Microsoft connector documentation](https://learn.microsoft.com/en-us/power-query/connectors/sharepointonlinelist) and [Power BI sharing requirements](https://learn.microsoft.com/en-us/power-bi/collaborate-share/service-share-dashboards).
5. **Do not publish synthetic Usage as real adoption.** Keep the demonstration report clearly labeled or remove its Adoption page. A future approved analytics export needs an observed source schema, permitted retention, pseudonymous user mapping, ActivityType and Outcome definitions, UTC conversion, deduplication key, coverage period and refresh owner. Copilot Studio sessions are not inferred from order counts. No automatic live usage feed exists in this kit. Live usage mapping and refresh remain Pending.

## Reconciliation and limits

| Measure | All-data synthetic expectation | Definition |
|---|---|---|
| Total / completed / active | 60 / 20 / 35 | Active excludes Completed and Cancelled |
| Completion rate | 0.333333 | 20 / 60; cancelled orders stay in denominator |
| On-time completion | 0.75 | 15 / 20 completed rows with both timestamps |
| Average cycle | 81 hours | Arithmetic mean initial SubmittedAt to CompletedAt |
| Approval turnaround | 12 hours | Mean of 35 successful matched approval events |
| Administrative rework | 15 orders; 0.25 | Distinct ChangesRequested orders / 60; excludes manual QC rework |
| Active overdue | 30 | Active DueAt strictly before 2026-10-14 12:00 UTC |
| Agent sessions | 114 | Independent synthetic Usage rows with AgentSession |
| Training completion | 9 / 12 = 0.75 | Successful training users / eligible cohort |

Weekly expectations and all status counts live in the JSON. Read [data notes](../data/README.md) for provenance and scenarios. The sample provides no true operational incident table. The Exceptions page uses synthetic scenario notes for illustration; a live incident register must be approved before an incident visual can claim real coverage. Snapshot paths are synthetic strings; they do not prove any files exist or were copied.
