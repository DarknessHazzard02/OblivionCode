Option Explicit

Public Sub RefreshAllPivotTablesInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentWorksheet As Worksheet
    Dim CurrentPivotTable As PivotTable

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = False

    '================================================================
    ' Refresh All Pivot Tables
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets
            For Each CurrentPivotTable In CurrentWorksheet.PivotTables
                On Error Resume Next
                CurrentPivotTable.RefreshTable
                On Error GoTo 0
            Next CurrentPivotTable
        Next CurrentWorksheet
    Next CurrentWorkbook

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "All Pivot Tables have been refreshed successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
