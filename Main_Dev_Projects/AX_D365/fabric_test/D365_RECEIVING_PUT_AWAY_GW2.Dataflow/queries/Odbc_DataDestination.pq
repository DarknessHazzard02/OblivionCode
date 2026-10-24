shared Odbc_DataDestination = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "<workspace-id-03>"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "<lakehouse-id-04>"]}[Data],
  TableNavigation = Navigation_2{[Id = "D365_RECEIVING_PUT_AWAY", ItemKind = "Table"]}[Data]
in
  TableNavigation;
