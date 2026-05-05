from __future__ import annotations

import subprocess


class LenaPermissionCenter:
    @staticmethod
    def probe() -> dict[str, bool]:
        permissions = {
            "accessibility": False,
            "automation": False,
            "microphone": False,
            "screen_recording": False,
        }

        try:
            proc = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of every process'],
                capture_output=True,
                text=True,
            )
            permissions["accessibility"] = proc.returncode == 0
            permissions["automation"] = proc.returncode == 0
        except Exception:
            pass

        return permissions
    