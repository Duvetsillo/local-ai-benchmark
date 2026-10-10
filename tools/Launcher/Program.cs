using System.Diagnostics;

namespace Launcher;

static class Program
{
    [STAThread]
    static void Main()
    {
        var installDirectory = AppContext.BaseDirectory;
        var scriptPath = Path.Combine(installDirectory, "Aetherion-License-Manager.ps1");
        if (!File.Exists(scriptPath))
        {
            MessageBox.Show(
                $"No se encontró el script principal en la carpeta de instalación:\n{scriptPath}",
                "Aetherion License Manager",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.Windows),
                "System32",
                "WindowsPowerShell",
                "v1.0",
                "powershell.exe"),
            WorkingDirectory = installDirectory,
            UseShellExecute = false,
            CreateNoWindow = true
        };
        startInfo.ArgumentList.Add("-NoLogo");
        startInfo.ArgumentList.Add("-NoProfile");
        startInfo.ArgumentList.Add("-ExecutionPolicy");
        startInfo.ArgumentList.Add("Bypass");
        startInfo.ArgumentList.Add("-File");
        startInfo.ArgumentList.Add(scriptPath);

        try
        {
            using var process = Process.Start(startInfo);
            if (process is null)
            {
                MessageBox.Show(
                    "No se pudo iniciar Windows PowerShell.",
                    "Aetherion License Manager",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
                return;
            }

            process.WaitForExit();
            Environment.Exit(process.ExitCode);
        }
        catch (Exception exception) when (exception is InvalidOperationException or System.ComponentModel.Win32Exception)
        {
            MessageBox.Show(
                $"No se pudo iniciar el administrador:\n{exception.Message}",
                "Aetherion License Manager",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
        }
    }
}