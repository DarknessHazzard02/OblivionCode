Option Explicit

Public Sub SetZoomTo85PercentInAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentWorksheet As Worksheet

    '================================================================
    ' Application Settings
    '================================================================
    Application.ScreenUpdating = False

    '================================================================
    ' Set Zoom Level To 85%
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets
            On Error Resume Next
            CurrentWorksheet.Activate
            ActiveWindow.Zoom = 85
            On Error GoTo 0
        Next CurrentWorksheet
    Next CurrentWorkbook

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "The zoom level has been set to 85% for all worksheets.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
