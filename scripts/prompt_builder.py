import os
import sys

from scripts.config import get_preference

from scripts.personality import NOVA_SYSTEM


def build_environment_context():
    """
    Tell Nova what host it is running on so it
    stops guessing shell syntax.
    """

    if sys.platform == "win32":

        home = os.environ.get(
            "USERPROFILE",
            "C:\\Users\\<username>",
        )

        return f"""

ENVIRONMENT
--------------------------------------------------

- Host OS: Windows (win32)
- Working directory: {os.getcwd()}
- User profile (home): {home}
- Downloads folder: {home}\\Downloads
- The shell tool runs through cmd.exe (Windows native).
- POSIX shell syntax NEVER works here: $HOME, ls, cat,
  head, grep, /mnt/..., ~/. These fail immediately.

Use cmd or PowerShell correctly:

1. Prefer cmd for simple file work:
   - dir, type, echo %USERPROFILE%
   - copy, mkdir, del

2. For PowerShell, ALWAYS invoke it explicitly and NEVER
   single-quote $env: variables. In single quotes
   PowerShell treats "$env" literally as a drive name
   (e.g. '$env:USERPROFILE' fails with
   "Cannot find drive").

3. Reliable path resolution on this machine:
   powershell -NoProfile -Command "[Environment]::GetFolderPath('UserProfile')"

4. Do not combine POSIX tools with Windows commands
   (pipes like | head fail).

5. Check the platform first when unsure, then commit to
   one Windows-native approach instead of guessing.
"""

    home = os.path.expanduser("~")

    return f"""

ENVIRONMENT
--------------------------------------------------

- Host OS: {os.name} ({sys.platform})
- Working directory: {os.getcwd()}
- User home: {home}

"""


def build_system_prompt():
    """
    Build Nova's system prompt based on the
    user's preference.
    """

    preference = get_preference()

    prompt = NOVA_SYSTEM + build_environment_context()

    if preference == "speed":
        prompt += """

Response Style:
- Keep answers short.
- Be direct.
- Avoid unnecessary explanations.
- Prioritize speed over depth.
"""

    elif preference == "balanced":
        prompt += """

Response Style:
- Give complete answers.
- Explain important decisions.
- Keep responses concise but informative.
"""

    elif preference == "deep":
        prompt += """

Response Style:
- Think like a senior engineer.
- Explain architecture.
- Mention tradeoffs.
- Mention performance.
- Mention maintainability.
- Mention security when relevant.
- Suggest improvements proactively.
- Act as an expert consultant.
"""

    return prompt