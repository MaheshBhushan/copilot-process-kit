# Dashboard specification

Use a 16:9 canvas with a consistent title, UTC refresh label, explicit AsOf cutoff and “Synthetic demonstration” banner. Use clear text labels and accessible contrast. Every status mark includes a name or icon plus name; color carries no exclusive meaning. Add descriptive visual titles, keyboard order and alt text. Restrict sharing through the approved workspace/dataset permissions.

## Operations page

Top row: Total Orders, Completed Orders, Active Orders, Active Overdue, Completion Rate. Second row: status distribution bar chart with labels and counts; backlog table showing OrderKey, Title, ProductType, Status, DueAt and Quantity. Apply active status filters to the backlog and sort DueAt ascending. Third row: On-time Completion %, Average Cycle Hours and weekly completion-date cycle trend using Cycle Hours by Completion Date. Use SubmittedDate slicers for cohort KPIs. Label the completion trend “completed during selected dates.” Include product and status slicers. Display the current AsOf cutoff beside overdue cards.

## Adoption page

Use Users Role and Date WeekStart slicers. Show Weekly Agent Users by WeekStart, Agent Sessions by WeekStart, Training Completion %, Training Completed Users and Eligible Pilot Users. Show ActivityType/Outcome counts in a supporting table. Keep the “Synthetic usage; no automatic Copilot analytics feed” banner visible. Never imply that failed sessions or order volume establish successful adoption. Training numerator uses the selected period; denominator uses the configured eligible cohort with role/user filters.

## Exceptions page

Show Approval Expiry Events, Administrative Rework Orders and Rework Rate. Show order drill-through with Events Revision, EventType, FromStatus, ToStatus, EventAt and ApprovalKey. Label event counts as submission-cohort history. Explain manual production QC rework separately; it creates no additional business transition. Illustrate file-copy and notification uncertainty with scenario notes beside the affected synthetic orders. Keep the live incidents panel marked “Pending: approved incident register.” Do not count scenario notes as observed operational incidents.

## Review checklist

Compare every card to expected-metrics.json with no filters. Compare the nine weekly user points individually. Confirm Approved keeps the requested ApprovalKey while its revision advances. Test date filters, cancelled orders in completion denominator, blank rates, overdue equality boundary and multi-selection/blank AsOf. Confirm adoption filters cannot multiply order/event counts. Record Desktop execution and tenant report reconciliation as Pending until observed.
