'================================================================
' Module_Template — <qué hace en una línea>
'================================================================
Option Explicit

Public Sub RunTemplate()
    '================================================================
    ' Variable Declaration
    '================================================================
    Dim CurrentWorkbook As Workbook
    Dim CurrentSheet As Worksheet
    Dim CurrentTable As ListObject
    Dim PreviousCalculation As XlCalculation

    On Error GoTo ErrorHandler

    '================================================================
    ' Application Settings
    '================================================================
    PreviousCalculation = Application.Calculation
    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.Calculation = xlCalculationManual

    '================================================================
    ' Logic
    '================================================================
    Set CurrentWorkbook = ThisWorkbook
    Set CurrentSheet = CurrentWorkbook.Worksheets("Data")
    Set CurrentTable = CurrentSheet.ListObjects("tblData")
    ' TODO: lógica sobre CurrentTable.DataBodyRange

CleanExit:
    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = PreviousCalculation
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    Exit Sub

ErrorHandler:
    MsgBox "RunTemplate falló: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume CleanExit
End Sub
'Made by: Hazzard
