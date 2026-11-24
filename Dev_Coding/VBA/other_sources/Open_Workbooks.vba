Option Explicit

Public Sub OpenAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim RootFolderPath As String

    '================================================================
    ' Initialize Variables
    '================================================================
    RootFolderPath = "C:\ruta\a\la\carpeta\"

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Open Master Files
    '================================================================
    Workbooks.Open RootFolderPath & "Master\Master_Template.xlsm"
    Workbooks.Open RootFolderPath & "Master\Oracle_Reports.xlsx"

    '================================================================
    ' Open Net Available Files
    '================================================================
    Workbooks.Open RootFolderPath & "Net Available\Master_Net_Available.xlsm"
    Workbooks.Open RootFolderPath & "Net Available\Net_Available_Table.xlsx"

    '================================================================
    ' Open Stockout Availability Files
    '================================================================
    Workbooks.Open RootFolderPath & "Stockout Availability\Master_Stockout_Availability.xlsm"

    '================================================================
    ' Open Order Closure Files
    '================================================================
    Workbooks.Open RootFolderPath & "Order Closure\Order_Closure.xlsx"

    '================================================================
    ' Restore Application Settings
    '================================================================
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True

    '================================================================
    ' Completion Message
    '================================================================
    'MsgBox "All workbooks have been opened successfully.", vbInformation, "Process Complete"

End Sub

'Made by: Hazzard
