Set ws = CreateObject("WScript.Shell")
ws.Run "cmd /c cd /d """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & """ && python app.py", 0, False
WScript.Sleep 3000
ws.Run "cmd /c start http://127.0.0.1:5001/", 0, False
