Option Explicit

Public Sub GoToFirstSheetInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook

    '================================================================
    ' Application Settings
    '================================================================
    Application.ScreenUpdating = False

    '================================================================
    ' Go To First Worksheet In All Workbooks
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        On Error Resume Next
        CurrentWorkbook.Worksheets(1).Activate
        On Error GoTo 0
    Next CurrentWorkbook

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "The first worksheet has been activated in all workbooks.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
