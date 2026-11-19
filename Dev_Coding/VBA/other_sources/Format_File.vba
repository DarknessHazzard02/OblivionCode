Option Explicit

Public Sub FormatAllSheetsInAllWorkbooks()

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
    ' Format All Worksheets
    '================================================================
    For Each CurrentWorkbook In Application.Workbooks
        For Each CurrentWorksheet In CurrentWorkbook.Worksheets

            With CurrentWorksheet.Cells
                .HorizontalAlignment = xlCenter
                .VerticalAlignment = xlCenter
                .Font.Name = "Calibri"
                .Font.Size = 10
            End With

            On Error Resume Next
            CurrentWorksheet.Activate
            ActiveWindow.DisplayGridlines = False
            CurrentWorksheet.Range("A1").Select
            On Error GoTo 0

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
    'MsgBox "All worksheets have been formatted successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
