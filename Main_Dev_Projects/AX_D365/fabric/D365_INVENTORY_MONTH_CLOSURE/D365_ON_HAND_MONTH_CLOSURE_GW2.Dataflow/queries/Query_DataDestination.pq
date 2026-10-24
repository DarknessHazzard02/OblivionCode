shared Query_DataDestination = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "<workspace-id>"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "<lakehouse-id>"]}[Data],
  TableNavigation = Navigation_2{[Id = "D365_ON_HAND", ItemKind = "Table"]}[Data]
in
  TableNavigation;
