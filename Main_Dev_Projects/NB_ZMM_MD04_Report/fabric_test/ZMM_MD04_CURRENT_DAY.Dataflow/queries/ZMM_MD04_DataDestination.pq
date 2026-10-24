shared ZMM_MD04_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null, EnableVorder = true, OutputMetadataRefresh = true]),
  Navigation_1 = Pattern{[workspaceId = "<workspace-id-03>"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "<lakehouse-id-04>"]}[Data],
  TableNavigation = Navigation_2{[Id = "SAP_ZMM_MD04", ItemKind = "Table"]}[Data]
in
  TableNavigation;
