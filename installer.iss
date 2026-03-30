; installer.iss - Version robuste avec association .lst (SANS code Pascal)
[Setup]
AppName=Lista State
AppVersion={#VERSION}
AppPublisher=Université du Burundi
AppPublisherURL=https://github.com/frasasu/lista_state
AppSupportURL=https://github.com/frasasu/lista_state
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

; === MÉTADONNÉES POUR L'ASSOCIATION DE FICHIERS ===
VersionInfoCompany=Université du Burundi
VersionInfoDescription=Lista State - Statistical Data Analysis
VersionInfoVersion={#VERSION}
VersionInfoProductName=Lista State

[Files]
; Icône unique pour tout
Source: "app\assets\monicone.ico"; DestDir: "{app}"; DestName: "monicone.ico"; Flags: ignoreversion

; Application (TOUS les fichiers générés par PyInstaller)
Source: "dist\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Raccourcis dans le menu Démarrer
Name: "{group}\Lista State"; Filename: "{app}\ListaState.exe"; IconFilename: "{app}\monicone.ico"; Comment: "Lancer Lista State"
Name: "{group}\Documentation"; Filename: "{app}\README.md"; IconFilename: "{app}\monicone.ico"
Name: "{group}\Uninstall Lista State"; Filename: "{uninstallexe}"; IconFilename: "{app}\monicone.ico"

; Raccourci sur le bureau (optionnel)
Name: "{autodesktop}\Lista State"; Filename: "{app}\ListaState.exe"; IconFilename: "{app}\monicone.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
Name: "associate_lst"; Description: "Associate .lst files with Lista State"; GroupDescription: "File associations:"; Flags: checkedonce

[Registry]
; === ASSOCIATION ROBUSTE DE L'EXTENSION .lst ===

; ÉTAPE 1: Définir l'extension .lst
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: ""; ValueData: "ListaState.File"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-lista-state"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCR; Subkey: ".lst"; ValueType: string; ValueName: "PerceivedType"; ValueData: "document"; Flags: uninsdeletevalue; Tasks: associate_lst

; ÉTAPE 2: Définir le type de fichier
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: ""; ValueData: "Lista State Session File"; Flags: uninsdeletekey; Tasks: associate_lst
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "Lista State Session"; Flags: uninsdeletekey; Tasks: associate_lst
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: "InfoTip"; ValueData: "Lista State session file containing tables and analyses"; Flags: uninsdeletekey; Tasks: associate_lst

; ÉTAPE 3: Assigner une icône aux fichiers .lst
Root: HKCR; Subkey: "ListaState.File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\monicone.ico,0"; Flags: uninsdeletekey; Tasks: associate_lst

; ÉTAPE 4: Définir la commande d'ouverture (double-clic)
Root: HKCR; Subkey: "ListaState.File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ListaState.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: associate_lst

; ÉTAPE 5: Ajouter au menu contextuel "Ouvrir avec"
Root: HKCR; Subkey: "Applications\ListaState.exe\SupportedTypes"; ValueType: string; ValueName: ".lst"; ValueData: ""; Flags: uninsdeletekey; Tasks: associate_lst

; ÉTAPE 6: Définir une description pour le type de fichier
Root: HKCR; Subkey: "ListaState.File"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "Lista State"; Flags: uninsdeletekey; Tasks: associate_lst

; === POUR L'UTILISATEUR COURANT ÉGALEMENT (HKCU) ===
Root: HKCU; Subkey: "Software\Classes\.lst"; ValueType: string; ValueName: ""; ValueData: "ListaState.File"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\.lst"; ValueType: string; ValueName: "Content Type"; ValueData: "application/x-lista-state"; Flags: uninsdeletevalue; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\ListaState.File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\monicone.ico,0"; Flags: uninsdeletekey; Tasks: associate_lst
Root: HKCU; Subkey: "Software\Classes\ListaState.File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\ListaState.exe"" ""%1"""; Flags: uninsdeletekey; Tasks: associate_lst

[Run]
; Option pour lancer l'application après installation
Filename: "{app}\ListaState.exe"; Description: "Launch Lista State"; Flags: nowait postinstall
