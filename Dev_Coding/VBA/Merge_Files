Option Explicit

Public Sub MergeFilesIntoSeparateSheets()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim FolderPath As String
    Dim CurrentFileName As String
    Dim SourceWorkbook As Workbook
    Dim SourceWorksheet As Worksheet
    Dim TargetWorkbook As Workbook

    '================================================================
    ' Select Source Folder
    '================================================================
    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = "Select Folder with the Excel Files"
        If .Show <> -1 Then Exit Sub
        FolderPath = .SelectedItems(1) & "\"
    End With

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    '================================================================
    ' Create Target Workbook
    '================================================================
    Set TargetWorkbook = Workbooks.Add(xlWBATWorksheet)

    On Error Resume Next
    TargetWorkbook.Sheets(1).Delete
    On Error GoTo 0

    '================================================================
    ' Copy Source Files Into Separate Worksheets
    '================================================================
    CurrentFileName = Dir(FolderPath & "*.xls*")

    Do While CurrentFileName <> ""

        Set SourceWorkbook = Workbooks.Open(FolderPath & CurrentFileName)
        Set SourceWorksheet = SourceWorkbook.Worksheets(1)

        SourceWorksheet.Copy After:=TargetWorkbook.Sheets(TargetWorkbook.Sheets.Count)

        On Error Resume Next
        TargetWorkbook.Sheets(TargetWorkbook.Sheets.Count).Name = Left(CurrentFileName, InStrRev(CurrentFileName, ".") - 1)
        On Error GoTo 0

        SourceWorkbook.Close SaveChanges:=False

        CurrentFileName = Dir

    Loop

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "All files have been merged into separate worksheets successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
