
Sub LinkedinSaveAllSelectedAsCleanHTML()
    Dim objApp As Outlook.Application
    Dim objSelection As Outlook.Selection
    Dim objItem As Object
    Dim mail As Outlook.MailItem
    Dim fso As Object
    Dim ts As Object
    Dim savePath As String
    Dim fileName As String
    Dim rawHtml As String
    Dim savedCount As Long
    
    ' Set your preferred output folder here (ensure trailing backslash) for your own automation projects BUT
    ' Don't change it for Linkedin job alerts email parser tool!
	
    savePath = "C:\SavedEmails\Linkedin-parser\"
    
    Set objApp = Outlook.Application
    Set objSelection = objApp.ActiveExplorer.Selection
    
    ' Initialize counter
    savedCount = 0
    
    ' Create FileSystemObject to handle text writing
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Ensure the export directory exists
    If Not fso.FolderExists(savePath) Then
        fso.CreateFolder (savePath)
    End If
    
    ' Check if anything is selected
    If objSelection.Count > 0 Then
        
        ' Loop through every item in your selection
        For Each objItem In objSelection
            
            ' Only process if the item is a standard email message
            If TypeOf objItem Is Outlook.MailItem Then
                Set mail = objItem
                
                ' Sanitize subject line to create a valid file name
                fileName = mail.Subject
                fileName = Replace(fileName, "\", "")
                fileName = Replace(fileName, "/", "")
                fileName = Replace(fileName, ":", "")
                fileName = Replace(fileName, "*", "")
                fileName = Replace(fileName, "?", "")
                fileName = Replace(fileName, """", "")
                fileName = Replace(fileName, "<", "")
                fileName = Replace(fileName, ">", "")
                fileName = Replace(fileName, "|", "")
                
                ' Append a timestamp to prevent accidental mixing of different emails with identical subjects
                fileName = Format(mail.ReceivedTime, "yyyy-mm-dd_hhnnss_") & fileName & ".html"
                
                ' BYPASS WORD: Grab the raw internal HTML string data
                rawHtml = mail.HTMLBody
                
                ' OVERWRITE ENFORCED: Setting the second parameter to True enforces an unconditional silent overwrite
                Set ts = fso.CreateTextFile(savePath & fileName, True, True)
                ts.Write rawHtml
                ts.Close
                
                ' Increment counter
                savedCount = savedCount + 1
            End If
        Next objItem
        
        ' End of cycle notification
        If savedCount > 0 Then
            MsgBox "Process complete!" & vbCrLf & _
                   "Successfully saved " & savedCount & " clean HTML files to: " & savePath, _
                   vbInformation, "Export Success"
        Else
            MsgBox "No valid email messages were found in your selection.", vbExclamation, "No Emails Saved"
        End If
        
    Else
        MsgBox "Please select at least one email message to export.", vbExclamation, "No Selection Found"
    End If
    
    ' Clean up memory references
    Set ts = Nothing
    Set fso = Nothing
    Set objItem = Nothing
    Set objSelection = Nothing
    Set objApp = Nothing
End Sub






