// Query name: SharePointSources. Text parameters: SiteUrl, OrdersListId, EventsListId.
// Logical parameter SharePointNaiveIsUtc defaults false. Set true only after proving returned naive values represent UTC.
// GUIDs must exactly match the Id values inspected in Navigator, including its formatting.
let
    Source = SharePoint.Tables(SiteUrl, [Implementation="2.0", ViewMode="All"]),
    OrdersRaw = Source{[Id=OrdersListId]}[Items],
    EventsRaw = Source{[Id=EventsListId]}[Items]
in
    [Orders=fxPrepare(OrdersRaw, "Orders", SharePointNaiveIsUtc),
     Events=fxPrepare(EventsRaw, "Events", SharePointNaiveIsUtc)]
