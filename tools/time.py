from datetime import datetime, timedelta
from tools.base import Tool


class TimeTool(Tool):

    name = "time"

    description = (
        "Current date and time: local ISO time, Unix "
        "timestamp, or date arithmetic."
    )

    def run(
        self,
        action="now",
        days=0,
        hours=0,
        minutes=0,
    ):

        if action == "unix":
            return str(int(datetime.now().timestamp()))

        if action == "now":
            now = datetime.now()

            return (
                f"{now.isoformat(timespec='seconds')} "
                f"({now.strftime('%A')})"
            )

        if action == "date":
            try:
                target = datetime.now() + timedelta(
                    days=float(days or 0),
                    hours=float(hours or 0),
                    minutes=float(minutes or 0),
                )
            except (TypeError, ValueError):
                return "days, hours and minutes must be numbers."

            return target.isoformat(timespec="seconds")

        raise ValueError(f"Unknown action: {action}")
