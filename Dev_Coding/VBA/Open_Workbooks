Option Explicit

Public Sub OpenAllWorkbooks()

    '================================================================
    ' Variable Declaration
    '================================================================
    Dim RootFolderPath As String

    '================================================================
    ' Initialize Variables
    '================================================================
    RootFolderPath = "C:\Users\NMC08UG\OneDrive - Nidec\MASTER - MASTER\"

    '================================================================
    ' Application Settings
    '================================================================
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False

    '================================================================
    ' Open Master Files
    '================================================================
    Workbooks.Open RootFolderPath & "MASTER\Master Motores Template.xlsm"
    Workbooks.Open RootFolderPath & "MASTER\Oracle_Wands_All_Reports.xlsx"

    '================================================================
    ' Open Net Available Files
    '================================================================
    Workbooks.Open RootFolderPath & "Net Available\Master_Net_Avail_Echo.xlsm"
    Workbooks.Open RootFolderPath & "Net Available\Net_Avail_Table_Alpha.xlsx"

    '================================================================
    ' Open Stockout Availability Files
    '================================================================
    Workbooks.Open RootFolderPath & "Stockout Availability\Master_Stockout_Availability.xlsm"

    '================================================================
    ' Open Order Closure Files
    '================================================================
    Workbooks.Open RootFolderPath & "Order Closure\NMC C15 Order Closure_V2.xlsx"

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
