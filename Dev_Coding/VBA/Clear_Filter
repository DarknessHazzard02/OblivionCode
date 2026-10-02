Option Explicit

Public Sub ClearAllFiltersInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentWorksheet As Worksheet
    Dim CurrentTable As ListObject

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Clear All Filters
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets

            If CurrentWorksheet.AutoFilterMode Then
                CurrentWorksheet.AutoFilterMode = False
            End If

            For Each CurrentTable In CurrentWorksheet.ListObjects
                If CurrentTable.ShowAutoFilter Then
                    On Error Resume Next
                    CurrentTable.AutoFilter.ShowAllData
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
    'MsgBox "All filters have been cleared successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
