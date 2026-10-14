// Query name: ApprovalFacts. Events must already reference LocalSources[Events] or SharePointSources[Events].
let
    Requests = Table.SelectColumns(Table.SelectRows(Events, each [EventType]="Validate"), {"ApprovalKey", "OrderKey", "EventAt"}),
    UniqueRequests = if Table.RowCount(Requests)=Table.RowCount(Table.Distinct(Requests, {"ApprovalKey"})) then Requests
                     else error "Duplicate approval request key; reconcile event history",
    Decisions = Table.SelectColumns(Table.SelectRows(Events, each [EventType]="ApprovalApproved"), {"EventKey", "OrderKey", "ApprovalKey", "EventAt"}),
    Joined = Table.NestedJoin(Decisions, {"ApprovalKey", "OrderKey"}, UniqueRequests, {"ApprovalKey", "OrderKey"}, "Request", JoinKind.LeftOuter),
    Checked = if List.AllTrue(List.Transform(Joined[Request], each Table.RowCount(_)=1)) then Joined
              else error "Successful approval must match exactly one request",
    Expanded = Table.ExpandTableColumn(Checked, "Request", {"EventAt"}, {"RequestedAt"}),
    Elapsed = Table.AddColumn(Expanded, "ApprovalHours", each Duration.TotalHours([EventAt]-[RequestedAt]), type number),
    Result = if List.AllTrue(List.Transform(Elapsed[ApprovalHours], each _>=0 and _<=72)) then Elapsed
             else error "Approval decision outside request deadline; reconcile history"
in Result
