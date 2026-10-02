Option Explicit

Public Sub RefreshAllPowerQueriesInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentWorksheet As Worksheet
    Dim CurrentTable As ListObject
    Dim CurrentConnection As WorkbookConnection

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Refresh Workbook Connections
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentConnection In CurrentWorkbook.Connections
            If CurrentConnection.Type = xlConnectionTypeMODEL Or CurrentConnection.Type = xlConnectionTypeOLEDB Then
                On Error Resume Next
                CurrentConnection.Refresh
                On Error GoTo 0
            End If
        Next CurrentConnection

        '============================================================
        ' Refresh Power Query Tables
        '============================================================
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets
            For Each CurrentTable In CurrentWorksheet.ListObjects
                If CurrentTable.SourceType = xlSrcQuery Then
                    On Error Resume Next
                    CurrentTable.QueryTable.Refresh BackgroundQuery:=False
                    On Error GoTo 0
                End If
            Next CurrentTable
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
    'MsgBox "All Power Queries have been refreshed successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
