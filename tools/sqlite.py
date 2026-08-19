import sqlite3
from pathlib import Path

from tools.base import Tool


class SqliteTool(Tool):

    name = "sqlite"

    description = (
        "Read SQLite databases read-only: list tables, "
        "show schema, or run SELECT/PRAGMA queries."
    )

    READ_ONLY_PREFIXES = ("select", "pragma", "explain", "with")

    def run(
        self,
        action,
        path,
        sql=None,
        limit=100,
    ):

        db = Path(path)

        if not db.exists():
            return f"Database not found: {path}"

        try:
            connection = sqlite3.connect(
                f"file:{db.resolve()}?mode=ro",
                uri=True,
            )
        except sqlite3.Error as exc:
            return f"Cannot open database: {exc}"

        try:
            if action == "tables":
                rows = connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' ORDER BY name"
                ).fetchall()

                return (
                    "\n".join(name for (name,) in rows)
                    if rows
                    else "(no tables)"
                )

            if action == "schema":
                rows = connection.execute(
                    "SELECT type, name, sql FROM sqlite_master "
                    "ORDER BY type, name"
                ).fetchall()

                if not rows:
                    return "(empty database)"

                lines = []

                for kind, name, definition in rows:
                    lines.append(f"-- {kind}: {name}")

                    if definition:
                        lines.append(definition)

                return "\n\n".join(lines)[:12000]

            if action == "query":
                if not sql:
                    raise ValueError("Query requires a sql.")

                statement = sql.strip().lower()

                if not statement.startswith(self.READ_ONLY_PREFIXES):
                    return (
                        "Only read-only queries are allowed "
                        "(SELECT/PRAGMA/EXPLAIN/WITH)."
                    )

                try:
                    cursor = connection.execute(sql)
                    rows = cursor.fetchall()

                except sqlite3.Error as exc:
                    return f"Query failed: {exc}"

                columns = (
                    [description[0] for description in cursor.description]
                    if cursor.description
                    else []
                )

                count = max(1, min(int(limit), 500))
                rows = rows[:count]

                if not rows:
                    return "Query returned no rows."

                if not columns:
                    return (
                        f"{len(rows)} row(s) returned:\n\n"
                        + "\n".join(str(row) for row in rows)
                    )

                widths = [
                    max(
                        len(columns[i]),
                        *(len(str(row[i])) for row in rows),
                    )
                    for i in range(len(columns))
                ]

                lines = []

                header = " | ".join(
                    columns[i].ljust(widths[i])
                    for i in range(len(columns))
                )
                lines.append(header)
                lines.append("-" * len(header))

                for row in rows:
                    lines.append(
                        " | ".join(
                            str(row[i]).ljust(widths[i])
                            for i in range(len(columns))
                        )
                    )

                return "\n".join(lines)

            raise ValueError(f"Unknown action: {action}")

        finally:
            connection.close()
