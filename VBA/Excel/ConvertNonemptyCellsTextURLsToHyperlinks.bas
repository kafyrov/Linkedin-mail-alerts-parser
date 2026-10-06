
Sub ConvertNonemptyCellsTextURLsToHyperlinks()

    Dim ws As Worksheet
    Dim cell As Range
    Dim url As String

    For Each ws In ActiveWorkbook.Worksheets
        For Each cell In ws.UsedRange

            If Not IsEmpty(cell.Value) Then
                url = CStr(cell.Value)

                ' Check if cell contains a URL
                If LCase(url) Like "http://*" Or LCase(url) Like "https://*" Then

                    ' Avoid double-creating hyperlinks
                    If cell.Hyperlinks.Count = 0 Then
                        ws.Hyperlinks.Add Anchor:=cell, Address:=url, TextToDisplay:=url
                    End If

                End If
            End If

        Next cell
    Next ws

End Sub
