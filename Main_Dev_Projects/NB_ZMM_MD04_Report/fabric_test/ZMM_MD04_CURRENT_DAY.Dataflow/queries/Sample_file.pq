shared #"Sample file" = let
  Source = Folder.Files("\\files.contoso-motors.example\shared\Logistics\BI Reports\ZMM_MD04"),
  #"Filtered hidden files" = Table.SelectRows(Source, each [Attributes]?[Hidden]? <> true),
  Navigation = #"Filtered hidden files"{[#"Folder Path" = "\\files.contoso-motors.example\shared\Logistics\BI Reports\ZMM_MD04\", Name = "MMD142_USALL_ZMMMD04_2023-08-31_06-10-21.txt"]}[Content]
in
  Navigation;
