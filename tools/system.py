import ctypes
import os
import platform
import shutil
import string

from tools.base import Tool


class SystemTool(Tool):

    name = "system"

    description = (
        "System information: OS, CPU, memory, disk "
        "usage and uptime."
    )

    def run(
        self,
        action="overview",
    ):

        if action == "cpu":
            return (
                f"CPU: {os.cpu_count()} cores · "
                f"{platform.processor() or 'unknown'} · "
                f"{platform.machine()}"
            )

        if action == "memory":
            total, available = self._memory()

            return (
                f"Memory: {self._fmt(available)} free "
                f"of {self._fmt(total)} "
                f"({self._percent(total, available)}% used)"
            )

        if action == "disk":
            lines = []

            for drive in self._drives():
                try:
                    usage = shutil.disk_usage(drive)
                except OSError:
                    continue

                lines.append(
                    f"{drive}: {self._fmt(usage.free)} free "
                    f"of {self._fmt(usage.total)} "
                    f"({self._percent(usage.total, usage.free)}% used)"
                )

            return "\n".join(lines) if lines else "(no drives)"

        if action == "uptime":
            return f"Uptime: {self._fmt_uptime()}"

        if action == "overview":
            total, available = self._memory()

            return (
                f"OS: {platform.system()} {platform.release()}\n"
                f"Python: {platform.python_version()}\n"
                f"CPU: {os.cpu_count()} cores · "
                f"{platform.machine()}\n"
                f"Memory: {self._fmt(available)} free "
                f"of {self._fmt(total)} "
                f"({self._percent(total, available)}% used)\n"
                f"Uptime: {self._fmt_uptime()}\n"
                f"Disk:\n"
                + "\n".join(
                    f"  {line}" for line in self.run("disk").splitlines()
                )
            )

        raise ValueError(f"Unknown action: {action}")

    @staticmethod
    def _memory():
        if os.name == "nt":
            class _MemoryStatusEx(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            status = _MemoryStatusEx()
            status.dwLength = ctypes.sizeof(_MemoryStatusEx)

            if ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(status)
            ):
                return status.ullTotalPhys, status.ullAvailPhys

        return 0, 0

    @staticmethod
    def _drives():
        if os.name != "nt":
            return [os.path.expanduser("~")]

        return [
            f"{letter}:\\"
            for letter in string.ascii_uppercase
            if os.path.exists(f"{letter}:\\")
        ]

    @staticmethod
    def _fmt_uptime():
        if os.name == "nt":
            try:
                ms = ctypes.windll.kernel32.GetTickCount64()
                seconds = ms // 1000
            except Exception:
                return "unknown"
        else:
            seconds = 0

        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes = rem // 60

        return f"{days}d {hours}h {minutes}m"

    @staticmethod
    def _fmt(bytes_value):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if bytes_value < 1024 or unit == "TB":
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024

        return f"{bytes_value:.1f} TB"

    @staticmethod
    def _percent(total, free):
        if not total:
            return 0

        return round((total - free) / total * 100)
