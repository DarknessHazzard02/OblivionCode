shared NavigationQuery = let
  Source = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false])
in
  Source;
