Option Explicit

Public Sub UnhideAllRowsAndColumnsInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentWorksheet As Worksheet

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Unhide All Rows And Columns
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets
            With CurrentWorksheet
                .Rows.Hidden = False
                .Columns.Hidden = False
            End With
        Next CurrentWorksheet
    Next CurrentWorkbook

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "All rows and columns have been unhidden successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
