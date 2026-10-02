Option Explicit

Public Sub CloseAllOtherWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Close All Workbooks Except This Workbook
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        If CurrentWorkbook.Name <> ThisWorkbook.Name Then
            CurrentWorkbook.Close SaveChanges:=True
        End If
    Next CurrentWorkbook

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "All other workbooks have been closed successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
