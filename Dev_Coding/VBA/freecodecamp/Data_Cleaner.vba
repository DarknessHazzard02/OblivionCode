' FreeCodeCamp Excel VBA Course
' Project: Automated Data Cleaning & Header Formatting

Sub CleanAndFormatData()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim lastCol As Long
    
    Set ws = ActiveSheet
    
    ' Find boundaries
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    
    ' Format Header Row
    With ws.Range(ws.Cells(1, 1), ws.Cells(1, lastCol))
        .Font.Bold = True
        .Font.Color = RGB(255, 255, 255)
        .Interior.Color = RGB(31, 78, 120)
        .HorizontalAlignment = xlCenter
    End With
    
    ' Autofit Columns
    ws.Columns.AutoFit
    
    MsgBox "Data cleaning and formatting complete!", vbInformation, "FreeCodeCamp VBA"
End Sub
