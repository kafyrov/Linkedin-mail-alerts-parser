Sub FormatNonEmptyCells()

    Dim ws As Worksheet
    Dim c As Range
    Dim usedRng As Range

    Set ws = ActiveSheet
    Set usedRng = ws.UsedRange

    ' Apply all borders to non-empty cells in the used range
    For Each c In usedRng.Cells
        If Len(c.Value) > 0 Then
            With c.Borders
                .LineStyle = xlContinuous
                .Weight = xlThin
            End With
        End If
    Next c

    ' Make only non-empty cells in row 1 bold
    For Each c In ws.Rows(1).Cells
        If Len(c.Value) > 0 Then
            c.Font.Bold = True
        End If
    Next c

End Sub
