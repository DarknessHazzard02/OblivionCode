shared Query_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "<workspace-id-03>"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "<lakehouse-id-04>"]}[Data],
  TableNavigation = Navigation_2{[Id = "D365_ON_HAND", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
