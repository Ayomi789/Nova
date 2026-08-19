import json
import subprocess

from tools.base import Tool


class GithubTool(Tool):

    name = "github"

    description = (
        "GitHub through the gh CLI: list, view or create "
        "pull requests and issues, inspect the repo."
    )

    def run(
        self,
        action,
        number=None,
        title=None,
        body=None,
        base=None,
        head=None,
        limit=10,
    ):

        if action == "pr_list":
            args = [
                "pr", "list",
                "--json", "number,title,state,author,createdAt",
                "--limit", str(max(1, min(int(limit), 50))),
            ]
            rows = self._gh(args)

            if isinstance(rows, str):
                return rows

            lines = []

            for pr in rows:
                lines.append(
                    f"#{pr['number']} [{pr['state']}] {pr['title']} "
                    f"({pr['author']['login']})"
                )

            return "\n".join(lines) if lines else "No pull requests."

        if action == "pr_view":
            if not number:
                raise ValueError("pr_view requires a number.")

            info = self._gh([
                "pr", "view", str(number),
                "--json", "number,title,state,author,body,mergedAt",
            ])

            if isinstance(info, str):
                return info

            body_text = (info.get("body") or "").strip()

            return (
                f"PR #{info['number']} [{info['state']}] {info['title']}\n"
                f"Author: {info['author']['login']}"
                + (f"\n\n{body_text}" if body_text else "")
            )

        if action == "pr_create":
            if not title:
                raise ValueError("pr_create requires a title.")

            args = ["pr", "create", "--title", title]

            if body:
                args += ["--body", body]

            if base:
                args += ["--base", base]

            if head:
                args += ["--head", head]

            out = self._gh(args, json_output=False)

            return out if isinstance(out, str) else "Pull request created."

        if action == "issue_list":
            args = [
                "issue", "list",
                "--json", "number,title,state,author",
                "--limit", str(max(1, min(int(limit), 50))),
            ]
            rows = self._gh(args)

            if isinstance(rows, str):
                return rows

            lines = []

            for issue in rows:
                lines.append(
                    f"#{issue['number']} [{issue['state']}] "
                    f"{issue['title']} ({issue['author']['login']})"
                )

            return "\n".join(lines) if lines else "No issues."

        if action == "issue_view":
            if not number:
                raise ValueError("issue_view requires a number.")

            info = self._gh([
                "issue", "view", str(number),
                "--json", "number,title,state,author,body",
            ])

            if isinstance(info, str):
                return info

            body_text = (info.get("body") or "").strip()

            return (
                f"Issue #{info['number']} [{info['state']}] "
                f"{info['title']}\nAuthor: {info['author']['login']}"
                + (f"\n\n{body_text}" if body_text else "")
            )

        if action == "issue_create":
            if not title:
                raise ValueError("issue_create requires a title.")

            args = ["issue", "create", "--title", title]

            if body:
                args += ["--body", body]

            out = self._gh(args, json_output=False)

            return out if isinstance(out, str) else "Issue created."

        if action == "repo":
            info = self._gh([
                "repo", "view",
                "--json", "nameWithOwner,description,url,primaryLanguage,stargazerCount",
            ])

            if isinstance(info, str):
                return info

            return (
                f"{info.get('nameWithOwner', '?')} "
                f"({info.get('primaryLanguage', {}).get('name', '—')}) "
                f"★{info.get('stargazerCount', 0)}\n"
                f"{info.get('description', '')}\n"
                f"{info.get('url', '')}"
            )

        raise ValueError(f"Unknown action: {action}")

    @staticmethod
    def _gh(args, json_output=True):
        try:
            result = subprocess.run(
                ["gh", *args],
                capture_output=True,
                text=True,
                timeout=30,
            )

        except FileNotFoundError:
            return "GitHub CLI not found. Install with: winget install GitHub.cli"

        except (subprocess.TimeoutExpired, OSError) as exc:
            return f"gh failed: {exc}"

        if result.returncode != 0:
            message = (result.stderr or result.stdout or "").strip()

            return message or "gh failed."

        output = (result.stdout or "").strip()

        if not json_output:
            return output or "(no output)"

        try:
            return json.loads(output)
        except ValueError:
            return output or "[]"
