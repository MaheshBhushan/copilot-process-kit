// Query name: LocalSources. Create DataFolder as a Text parameter (absolute data folder, no trailing separator required).
let
    Read = (file as text, name as text) as table =>
        fxPrepare(Table.PromoteHeaders(Csv.Document(File.Contents(DataFolder & "/" & file),
            [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true]), name, false)
in
    [Orders=Read("Orders.csv", "Orders"), Events=Read("OrderEvents.csv", "Events"),
     Usage=Read("Usage.csv", "Usage"), Users=Read("Users.csv", "Users")]
