Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Obtém o diretório onde o script está localizado
CurrentDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = CurrentDir

' Executa o pythonw do ambiente virtual de forma oculta (0 = janela invisível)
PythonwPath = CurrentDir & "\venv\Scripts\pythonw.exe"
MainPyPath = CurrentDir & "\main.py"

If FSO.FileExists(PythonwPath) Then
    WshShell.Run """" & PythonwPath & """ """ & MainPyPath & """", 0, False
Else
    MsgBox "O ambiente virtual (venv) não foi encontrado na pasta." & vbCrLf & "Por favor, certifique-se de que a pasta venv existe em: " & CurrentDir, 16, "Calculadora Profissional - Erro"
End If
