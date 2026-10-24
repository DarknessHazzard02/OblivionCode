shared #"Transform Sample file" = let
  Source = Csv.Document(Parameter, [Delimiter = "|", Columns = 34, Encoding = 65001, QuoteStyle = QuoteStyle.None])
in
  Source;
[FunctionQueryBinding = "{""exemplarFormulaName"":""Transform Sample file""}"]
