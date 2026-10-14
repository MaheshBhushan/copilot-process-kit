// Query name: fxPrepare. Function shared by local and SharePoint sources.
(input as table, name as text, allowNaiveUtc as logical) as table =>
let
    Specifications = [
        Orders={{"Title", "Text"}, {"OrderKey", "Text"}, {"Status", "Choice"}, {"Revision", "Number"}, {"CustomerCode", "Text"}, {"ProductType", "Choice"}, {"Quantity", "Number"}, {"QuoteEUR", "Currency"}, {"DueAt", "DateTime"}, {"SubmittedAt", "DateTime"}, {"ApprovalRequestedAt", "DateTime"}, {"ApprovalDueAt", "DateTime"}, {"ApprovedAt", "DateTime"}, {"ProductionStartedAt", "DateTime"}, {"CompletedAt", "DateTime"}, {"CancelledAt", "DateTime"}, {"SalesUPN", "Text"}, {"ApproverUPN", "Text"}, {"ProductionUPN", "Text"}, {"DraftFilePath", "Text"}, {"ApprovalSnapshotPath", "Text"}, {"ReleasedFilePath", "Text"}, {"CustomerConsentRef", "Text"}, {"ApprovalKey", "Text"}, {"LastCommandKey", "Text"}, {"QCReference", "Text"}, {"WasteQuantity", "Number"}},
        Events={{"Title", "Text"}, {"EventKey", "Text"}, {"OrderKey", "Text"}, {"CommandID", "Number"}, {"FromStatus", "Text"}, {"ToStatus", "Text"}, {"Revision", "Number"}, {"EventAt", "DateTime"}, {"ActorUPN", "Text"}, {"Role", "Text"}, {"EventType", "Text"}, {"ApprovalKey", "Text"}, {"DurationHours", "Number"}},
        Users={{"UserKey", "Text"}, {"UPN", "Text"}, {"Role", "Text"}, {"EligiblePilot", "Boolean"}},
        Usage={{"EventID", "Text"}, {"EventAt", "DateTime"}, {"UserKey", "Text"}, {"Role", "Text"}, {"ActivityType", "Text"}, {"Outcome", "Text"}}
    ],
    Spec = Record.Field(Specifications, name),
    Project = Table.SelectColumns(input, List.Transform(Spec, each _{0}), MissingField.Error),
    Nulls = Table.ReplaceValue(Project, "", null, Replacer.ReplaceValue, Table.ColumnNames(Project)),
    Utc = (v as any) as nullable datetime =>
        if v = null then null else
        let Zoned = if Value.Is(v, type datetimezone) then v
                    else if Value.Is(v, type text) then
                        if Text.EndsWith(v, "Z") then DateTimeZone.FromText(v)
                        else error "Text timestamp must have explicit UTC Z suffix"
                    else if Value.Is(v, type datetime) and allowNaiveUtc then DateTime.AddZone(v, 0)
                    else error "Unverified unzoned timestamp; inspect SharePoint UTC semantics first"
        in DateTimeZone.RemoveZone(DateTimeZone.SwitchZone(Zoned, 0)),
    DateColumns = List.Transform(List.Select(Spec, each _{1}="DateTime"), each _{0}),
    Dates = Table.TransformColumns(Nulls, List.Transform(DateColumns, each {_, Utc, type nullable datetime})),
    Types = List.Transform(List.Select(Spec, each _{1}<>"DateTime"), each {_{0},
        if _{1}="Currency" then Currency.Type else if _{1}="Number" then
            (if _{0}="DurationHours" then type number else Int64.Type)
        else if _{1}="Boolean" then type logical else type text}),
    Typed = Table.TransformColumnTypes(Dates, Types, "en-US"),
    Result = if name="Orders" then
        Table.AddColumn(Table.AddColumn(Typed, "SubmittedDate", each Date.From([SubmittedAt]), type date),
            "CompletedDate", each if [CompletedAt]=null then null else Date.From([CompletedAt]), type nullable date)
        else if name="Events" or name="Usage" then
            Table.AddColumn(Typed, "EventDate", each Date.From([EventAt]), type date)
        else Typed
in Result
