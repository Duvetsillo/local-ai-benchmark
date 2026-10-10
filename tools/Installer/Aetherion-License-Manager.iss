#define AppName "Aetherion License Manager"
#define AppVersion "1.1.0"
#define AppPublisher "Aetherion"
#define AppExeName "Aetherion-License-Manager.exe"

[Setup]
AppId={{1F42CE85-C1F2-4F8A-A3BE-0AC9BD411891}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Aetherion License Manager
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
OutputDir=..\dist
OutputBaseFilename=Aetherion-License-Manager-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "..\Aetherion-License-Manager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Aetherion-License-Manager.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Aetherion-License-Manager.deps.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Aetherion-License-Manager.runtimeconfig.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Aetherion-License-Manager.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Aetherion-License-Manager.UI.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\Assets\Inter.ttf"; DestDir: "{app}\Assets"; Flags: ignoreversion
Source: "..\Assets\Inter-OFL.txt"; DestDir: "{app}\Assets"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: postinstall nowait skipifsilent

[Code]
function HasDesktopRuntimeAt(const RuntimeRoot: string): Boolean;
var
  FindRec: TFindRec;
begin
  Result := False;
  if FindFirst(AddBackslash(RuntimeRoot) + '8.*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
        begin
          Result := True;
          Exit;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

function IsDesktopRuntimeInstalled: Boolean;
var
  UserDotNetRoot: string;
begin
  UserDotNetRoot := AddBackslash(GetEnv('USERPROFILE')) + '.dotnet\shared\Microsoft.WindowsDesktop.App';
  Result :=
    HasDesktopRuntimeAt(ExpandConstant('{autopf}\dotnet\shared\Microsoft.WindowsDesktop.App')) or
    HasDesktopRuntimeAt(UserDotNetRoot);
end;

function InitializeSetup: Boolean;
var
  ErrorCode: Integer;
begin
  Result := IsDesktopRuntimeInstalled;
  if not Result then
  begin
    MsgBox(
      'Aetherion License Manager necesita .NET 8 Desktop Runtime (x64). Se abrirá la página oficial para instalarlo; después, vuelve a ejecutar el instalador.',
      mbError,
      MB_OK);
    ShellExec(
      'open',
      'https://dotnet.microsoft.com/en-us/download/dotnet/8.0/runtime',
      '',
      '',
      SW_SHOWNORMAL,
      ewNoWait,
      ErrorCode);
  end;
end;
