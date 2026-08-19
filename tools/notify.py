import os
import subprocess

from tools.base import Tool


class NotifyTool(Tool):

    name = "notify"

    description = (
        "Show a Windows desktop toast notification "
        "with a title and message."
    )

    def run(
        self,
        title="Nova",
        message="",
    ):

        title = (str(title) or "Nova")[:64]
        message = (str(message) or "")[:256]

        if os.name != "nt":
            return f"[notify] {title}: {message}"

        script = (
            "Add-Type -AssemblyName System.Windows.Forms\n"
            "Add-Type -AssemblyName System.Drawing\n"
            f"$n = New-Object System.Windows.Forms.NotifyIcon\n"
            f"$n.Icon = [System.Drawing.SystemIcons]::Information\n"
            f"$n.BalloonTipTitle = '{title.replace(chr(39), chr(39)*2)}'\n"
            f"$n.BalloonTipText = '{message.replace(chr(39), chr(39)*2)}'\n"
            f"$n.Visible = $true\n"
            f"$n.ShowBalloonTip(6000)\n"
            f"Start-Sleep -Seconds 7\n"
            f"$n.Dispose()\n"
        )

        try:
            subprocess.Popen(
                [
                    "powershell",
                    "-NoProfile",
                    "-WindowStyle", "Hidden",
                    "-Command", script,
                ],
                creationflags=0x08000000,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except OSError as exc:
            return f"Notification failed: {exc}"

        return "Notification shown."
