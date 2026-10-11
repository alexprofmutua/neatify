[Setup]
AppId={{6B9071C5-742D-4B44-A4D2-8D8F0B88F180}
AppName=Neatify
AppVersion=1.0.0
AppPublisher=Neatify
DefaultDirName={autopf}\Neatify
DefaultGroupName=Neatify
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=Neatify-Windows-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\Neatify\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Neatify"; Filename: "{app}\Neatify.exe"
Name: "{autodesktop}\Neatify"; Filename: "{app}\Neatify.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\Neatify.exe"; Description: "Launch Neatify"; Flags: nowait postinstall skipifsilent
