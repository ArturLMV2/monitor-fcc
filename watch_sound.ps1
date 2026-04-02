Add-Type -AssemblyName System.Windows.Forms

while ($true) {
    if (Test-Path "D:\git\monitor-fcc\data\alert.txt") {

        [console]::beep(1000,500)

        [System.Windows.Forms.MessageBox]::Show(
            "Nova publicacao detectada!",
            "Monitor FCC"
        )

        Remove-Item "D:\git\monitor-fcc\data\alert.txt"
    }

    Start-Sleep -Milliseconds 500
}