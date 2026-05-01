[Setup]
; --- 1. INFO BÁSICA ---
AppName=OrgPro
AppVersion=1.4
AppPublisher=Software Por Chris
AppCopyright=Copyright (C) 2026 Chris

; --- 2. CONFIGURACIÓN DE CARPETAS ---
DefaultDirName={autopf}\OrgPro
DisableProgramGroupPage=yes

; --- 3. SALIDA DEL INSTALADOR ---
; Salimos de la carpeta setup y creamos el instalador en la raíz
OutputDir=..\InstaladorFinal
OutputBaseFilename=Instalar_OrgPro
; Salimos de setup y entramos a assets
SetupIconFile=..\assets\icono.ico

; --- 4. ESTÉTICA E IMÁGENES ACTIVADAS ---
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Salimos de setup y entramos a assets para las imágenes
WizardImageFile=..\assets\bienvenida.bmp
WizardSmallImageFile=..\assets\logo_peq.bmp

; --- 5. EL IDIOMA (ESPAÑOL) ---
[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Salimos de setup y entramos a dist
Source: "..\dist\OrgPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\OrgPro"; Filename: "{app}\OrgPro.exe"; IconFilename: "{app}\OrgPro.exe"
Name: "{autodesktop}\OrgPro"; Filename: "{app}\OrgPro.exe"; IconFilename: "{app}\OrgPro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\OrgPro.exe"; Description: "{cm:LaunchProgram,OrgPro}"; Flags: nowait postinstall skipifsilent