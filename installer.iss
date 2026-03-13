; installer.iss
[Setup]
AppName=Lista State
AppVersion={#VERSION}
AppPublisher=Université du Burundi
AppPublisherURL=https://github.com/frasasu/lista-state
AppSupportURL=https://github.com/frasasu/lista-state
DefaultDirName={autopf}\ListaState
DefaultGroupName=Lista State
UninstallDisplayIcon={app}\ListaState.exe
SetupIconFile=app/assets/monicone.ico
OutputDir=installer
OutputBaseFilename=ListaState_Setup_{#VERSION}
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Files]
; Icône
Source: "app\assets\monicone.ico"; DestDir: "{app}"; DestName: "monicone.ico"; Flags: ignoreversion

; Application
Source: "dist\ListaState\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Lista State"; Filename: "{app}\ListaState.exe"; IconFilename: "{app}\monicone.ico"
Name: "{group}\Documentation"; Filename: "{app}\README.md"; IconFilename: "{app}\monicone.ico"
Name: "{group}\Uninstall Lista State"; Filename: "{uninstallexe}"; IconFilename: "{app}\monicone.ico"
Name: "{autodesktop}\Lista State"; Filename: "{app}\ListaState.exe"; IconFilename: "{app}\monicone.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
Name: "associate_lst"; Description: "Associate .lst files with Lista State"; GroupDescription: "File associations:"; Flags: checkedonce

[Registry]
; Définir le type de fichier
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: ""; ValueData: "ListaState.File"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-lista-state"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: "PerceivedType"; ValueData: "document"; Flags: uninsdeletevalue; Tasks: associate_lst

; Description du type de fichier
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: ""; ValueData: "Lista State Session File"; Flags: uninsdeletekey; Tasks: associate_lst
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Lista State Session"; Flags: uninsdeletekey; Tasks: associate_lst

; Icône pour les fichiers .lst
Root: HKCR; Subkey: "ListaState.File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\monicone.ico,0"; Flags: uninsdeletekey; Tasks: associate_lst

; Commande d'ouverture
Root: HKCR; Subkey: "ListaState.File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ListaState.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: associate_lst

; Ajouter au menu "Ouvrir avec"
Root: HKCR; Subkey: "Applications\ListaState.exe\SupportedTypes"; ValueType: string; ValueName: ".lst"; ValueData: ""; Flags: uninsdeletekey; Tasks: associate_lst

; Pour l'utilisateur courant également
Root: HKCU; Subkey: "Software\Classes\.lst"; ValueType: string; ValueName: ""; ValueData: "ListaState.File"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\.lst"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-lista-state"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\ListaState.File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\monicone.ico,0"; Flags: uninsdeletekey; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\ListaState.File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ListaState.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: associate_lst

[Run]
Filename: "{app}\ListaState.exe"; Description: "Launch Lista State"; Flags: nowait postinstall

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Notifier Windows que les associations ont changé
    ShellExec('open', 'rundll32.exe', 'shell32.dll,UpdatePerUserSystemNotifications', '', SW_HIDE, ewNoWait, 0);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Nettoyer les associations à la désinstallation
    RegDeleteKeyIncludingSubkeys(HKCR, '.lst');
    RegDeleteKeyIncludingSubkeys(HKCR, 'ListaState.File');
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\.lst');
    RegDeleteKeyIncludingSubkeys(HKCU, 'Software\Classes\ListaState.File');
    
    // Notifier Windows
    ShellExec('open', 'rundll32.exe', 'shell32.dll,UpdatePerUserSystemNotifications', '', SW_HIDE, ewNoWait, 0);
  end;
end;