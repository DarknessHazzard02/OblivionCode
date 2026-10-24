shared Query_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "<workspace-id>"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "<lakehouse-id>"]}[Data],
  TableNavigation = Navigation_2{[Id = "D365_INVOICING", ItemKind = "Table"]}[Data]
in
  TableNavigation;
